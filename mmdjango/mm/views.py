from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from mm.models import FBUser

import ast
import requests
import os
import os.path
import urllib
import json

FB_APP_ID = '274847765934546'
FB_APP_SECRET = '888949406beb1a60ce62963d679678f9'
FB_API_SCOPE = 'user_likes+friends_likes+user_interests+friends_interests+user_activities+friends_activities+publish_stream'
SECRET_CODE = None
requests = requests.session()

app_url = 'https://graph.facebook.com/{0}'.format(FB_APP_ID)
FB_APP_NAME = json.loads(requests.get(app_url).content).get('name')
COOKIE_TOKEN = 'fbapp' + FB_APP_ID + 'token'
COOKIE_FBID = 'fbapp' + FB_APP_ID + 'fbid'
question_mark_picture = 'http://local2social.com/wp-content/uploads/2011/02/questionmark.jpg'

# list of categories: [(display name, category name, url)]
categoryList = [('All Likes', 'likes', '/'), 
                ('Music', 'music', 'music'), 
                ('Movies', 'movies', 'movies'), 
                ('TV', 'television', 'tv'), 
                ('Books', 'books', 'books'), 
                ('Games', 'games', 'games'), 
                ('Interests', 'interests', 'interests'), 
                ('Activities', 'activities', 'activities')]

def oauth_login_url(request):
    fb_login_uri = ("https://www.facebook.com/dialog/oauth"
                    "?client_id=%s&redirect_uri=%s&scope=%s" %
                    (FB_APP_ID, get_code_url(request), FB_API_SCOPE))

    return fb_login_uri

def simple_dict_serialisation(params):
    return "&".join(map(lambda k: "%s=%s" % (k, params[k]), params.keys()))

def fbapi_get_string(path, domain=u'graph', params=None, access_token=None, encode_func=urllib.urlencode):
    if not params:
        params = {}
    params[u'method'] = u'GET'
    if access_token:
        params[u'access_token'] = access_token

    for k, v in params.iteritems():
        if hasattr(v, 'encode'):
            params[k] = v.encode('utf-8')

    url = u'https://' + domain + u'.facebook.com' + path
    params_encoded = encode_func(params)
    url = url + params_encoded
    result = requests.get(url).content

    return result

def fbapi_auth(code, request):
    params = {'client_id': FB_APP_ID,
              'redirect_uri': get_code_url(request),
              'client_secret': FB_APP_SECRET,
              'code': code}

    result = fbapi_get_string(path=u"/oauth/access_token?", params=params, encode_func=simple_dict_serialisation)

    pairs = result.split("&", 1)
    result_dict = {}
    for pair in pairs:
        (key, value) = pair.split("=")
        result_dict[key] = value
    return (result_dict["access_token"], result_dict["expires"])

def fbapi_get_application_access_token(id):
    token = fbapi_get_string(
        path=u"/oauth/access_token",
        params=dict(grant_type=u'client_credentials', client_id=id,
                    client_secret=app.config['FB_APP_SECRET']),
        domain=u'graph')

    token = token.split('=')[-1]
    if not str(id) in token:
        print 'Token mismatch: %s not in %s' % (id, token)
    return token

def fb_call(call, args=None):
    url = "https://graph.facebook.com/{0}".format(call)
    r = requests.get(url, params=args)
    return json.loads(r.content)

def fb_post(call, args=None):
    url = "https://graph.facebook.com/{0}".format(call)
    r = requests.post(url, params=args)
    return json.loads(r.content)

def get_home(request):
    return 'http://' + request.get_host() + '/'

def get_code_url(request):
    return get_home(request) + 'getcode'

# Gets token from code, saves token to cookie
def get_code(request):
    if request.GET.get('code', None):
        request.session[COOKIE_TOKEN] = fbapi_auth(request.GET.get('code'), request)[0]
    return redirect(get_home(request))

def music(request):
    return index(request, 'music')
def movies(request):
    return index(request, 'movies')
def tv(request):
    return index(request, 'television')
def books(request):
    return index(request, 'books')
def games(request):
    return index(request, 'games')
def interests(request):
    return index(request, 'interests')
def activities(request):
    return index(request, 'activities')

def index(request, category='likes'):
    access_token = request.session.get(COOKIE_TOKEN, None)
    
    if access_token:
        # Only do facebook api search if user refreshes or there is no data in database
        do_api_search = request.POST.get('refresh', False)
        
        me = {}
        friendsData = {}
        myData = {}
        recommendedList = []
        friendsList = []
        haveCategory, hasRecommended = False, False
        
        if not do_api_search:
            user_id = request.session.get(COOKIE_FBID, None)
            if user_id:
                try:
                    # Get category data from database
                    user = FBUser.objects.get(pk=user_id)
                    userCategoryData = None
                    friendCategoryData = None
                    recommendedData = None
                    friendsListData = None
                    
                    if category == 'music':
                        userCategoryData = user.music_data
                        friendCategoryData = user.music_friend_data
                        recommendedData = user.music_recommended_data
                        friendsListData = user.music_friendslist_data
                    elif category == 'movies':
                        userCategoryData = user.movies_data
                        friendCategoryData = user.movies_friend_data
                        recommendedData = user.movies_recommended_data
                        friendsListData = user.movies_friendslist_data
                    elif category == 'television':
                        userCategoryData = user.tv_data
                        friendCategoryData = user.tv_friend_data
                        recommendedData = user.tv_recommended_data
                        friendsListData = user.tv_friendslist_data
                    elif category == 'books':
                        userCategoryData = user.books_data
                        friendCategoryData = user.books_friend_data
                        recommendedData = user.books_recommended_data
                        friendsListData = user.books_friendslist_data
                    elif category == 'games':
                        userCategoryData = user.games_data
                        friendCategoryData = user.games_friend_data
                        recommendedData = user.games_recommended_data
                        friendsListData = user.games_friendslist_data
                    elif category == 'interests':
                        userCategoryData = user.interests_data
                        friendCategoryData = user.interests_friend_data
                        recommendedData = user.interests_recommended_data
                        friendsListData = user.interests_friendslist_data
                    elif category == 'activities':
                        userCategoryData = user.activities_data
                        friendCategoryData = user.activities_friend_data
                        recommendedData = user.activities_recommended_data
                        friendsListData = user.activities_friendslist_data
                    elif category == 'likes':
                        userCategoryData = user.likes_data
                        friendCategoryData = user.likes_friend_data
                        recommendedData = user.likes_recommended_data
                        friendsListData = user.likes_friendslist_data
                    
                    if userCategoryData and friendCategoryData and recommendedData and friendsListData:
                        me = ast.literal_eval(user.me_data)
                        myData = ast.literal_eval(userCategoryData)
                        friendsData = ast.literal_eval(friendCategoryData)
                        recommendedList = ast.literal_eval(recommendedData)
                        friendsList = ast.literal_eval(friendsListData)
                        haveCategory = (len(myData['data']) > 0)
                        hasRecommended = (len(recommendedList) > 0)
                except:
                    do_api_search = True
            else:
                do_api_search = True
        
        if do_api_search:
            me = fb_call('me', args={'access_token': access_token})
            if not me:
                return redirect(get_home(request))
            friendsData = fb_call('me/friends', args={'fields': 'name,picture,'+category, 'access_token': access_token})        
            myData = fb_call('me/'+category, args={'access_token': access_token})

            # Save cookie
            request.session[COOKIE_FBID] = me['id']
        
            myThings = {} # List of my things
            recommended = {} # Dict of recommended category: {thing name: [rating, id]}
            friends = {} # Dict of friends: {friend id: [name, picture, common things]}
        
            # Gets my list of things if I have any
            if myData.has_key('data') and len(myData['data']) > 0:
                haveCategory = True
                for m in myData['data']:
                    myThings[m['name']] = m['id']
            
            if friendsData.has_key('data'):
                for f in friendsData['data']:
                    friends[f['id']] = [f['name'], f['picture']]
                    
                    # Skip empty things data
                    if not f.get(category):
                        friends[f['id']].append(None)
                        continue
                    
                    # Gets list of friend things
                    friendThings = {}
                    for m in f[category]['data']:
                        friendThings[m['name']] = m['id']
                        
                    # Finds common things between me and friend
                    # Sets weight to 1 if I have no things, or to the number of things we have in common
                    common = []
                    weight = 1
                    if haveCategory:
                        common = set(myThings) & set(friendThings)
                        weight = len(common)/float(len(friendThings))
                    friends[f['id']].extend([len(common), list(common)])
                    
                    # If we have things in common or I have no things,
                    # then add all their things to recommended list and increment rating by weight
                    if len(common) > 0 or not haveCategory:
                        theirs = set(friendThings) - set(myThings)
                        for m in theirs:
                            recommended[m] = [recommended.get(m, [0])[0] + weight, friendThings[m]]
                        
            recommendedList = [] # Sorted list of recommended
            if len(recommended) > 0:
                hasRecommended = True
            
                # Limit recommended to top 200
                recommended = dict(sorted(recommended.iteritems(), key=lambda x: x[1][0], reverse=True)[0:200])
                
                # Construct query of all recommended things
                recommendedCategoryQuery = ''
                for m in recommended:
                    recommendedCategoryQuery += recommended[m][1] + ','
                
                # Add picture and link to recommended things
                categoryData = fb_call('?ids=' + recommendedCategoryQuery[:-1], args={'fields': 'name, picture, link', 'access_token': access_token})
                for m in categoryData:
                    recommended[categoryData[m]['name']].extend(
                    [categoryData[m]['picture'] if categoryData[m].has_key('picture') else question_mark_picture, categoryData[m]['link']])
                    
                # Add unknown picture and link
                for x in recommended:
                    if len(recommended[x]) <= 2:
                        recommended[x].extend([question_mark_picture, ''])
                    
                # Sort recommended thing list by rating
                recommendedList = sorted(recommended.iteritems(), key=lambda x: x[1][0], reverse=True)
                friendsList = sorted(friends.iteritems(), key=lambda x: x[1][2], reverse=True)
            
            # Save to database
            user = FBUser.objects.get_or_create(pk=me['id'])[0]
            user.me_data = me
            if category == 'music':
                user.music_friend_data = friendsData
                user.music_data = myData
                user.music_recommended_data = recommendedList
                user.music_friendslist_data = friendsList
            elif category == 'movies':
                user.movies_friend_data = friendsData
                user.movies_data = myData
                user.movies_recommended_data = recommendedList
                user.movies_friendslist_data = friendsList
            elif category == 'television':
                user.tv_friend_data = friendsData
                user.tv_data = myData
                user.tv_recommended_data = recommendedList
                user.tv_friendslist_data = friendsList
            elif category == 'books':
                user.books_friend_data = friendsData
                user.books_data = myData
                user.books_recommended_data = recommendedList
                user.books_friendslist_data = friendsList
            elif category == 'games':
                user.games_friend_data = friendsData
                user.games_data = myData
                user.games_recommended_data = recommendedList
                user.games_friendslist_data = friendsList
            elif category == 'interests':
                user.interests_friend_data = friendsData
                user.interests_data = myData
                user.interests_recommended_data = recommendedList
                user.interests_friendslist_data = friendsList
            elif category == 'activities':
                user.activities_friend_data = friendsData
                user.activities_data = myData
                user.activities_recommended_data = recommendedList
                user.activities_friendslist_data = friendsList
            elif category == 'likes':
                user.likes_friend_data = friendsData
                user.likes_data = myData
                user.likes_recommended_data = recommendedList
                user.likes_friendslist_data = friendsList
            user.save()

        return render_to_response('index.html', 
        {'app_id': FB_APP_ID, 'name': FB_APP_NAME, 'categoryList': categoryList, 'category': category, 'friendsList': friendsList, 'recommendedList': recommendedList[0:100], 'haveCategory': haveCategory, 'hasRecommended': hasRecommended})
    else:
        return redirect(oauth_login_url(request))

# API for searching friends for thing
def api(request):
    access_token = request.session.get(COOKIE_TOKEN, None)
    user_id = request.session.get(COOKIE_FBID, None)
    user = FBUser.objects.get(pk=user_id)
    searchThing = request.GET.get('q', None)
    category = request.GET.get('c', 'likes')
    if request.method == 'GET' and searchThing and user_id and user:# and request.is_ajax():
        # Get friend data from database
        friendCategoryData = None
        if category == 'music':
            friendCategoryData = user.music_friend_data
        elif category == 'movies':
            friendCategoryData = user.movies_friend_data
        elif category == 'television':
            friendCategoryData = user.tv_friend_data
        elif category == 'books':
            friendCategoryData = user.books_friend_data
        elif category == 'games':
            friendCategoryData = user.games_friend_data
        elif category == 'interests':
            friendCategoryData = user.interests_friend_data
        elif category == 'activities':
            friendCategoryData = user.activities_friend_data
        elif category == 'likes':
            friendCategoryData = user.likes_friend_data
            
        friendsData = ast.literal_eval(friendCategoryData)
        
        results = {}
        for f in friendsData['data']:
            # Skip empty category data
            if not f.get(category):
                continue
            
            # Gets list of friend things
            friendThings = {}
            for m in f[category]['data']:
                friendThings[m['name']] = m['id']
            # Searches friends things for thing and adds to results
            if friendThings.has_key(searchThing):
                del friendThings[searchThing]
                for m in friendThings:
                    results[m] = [results.get(m, [0])[0] + 1, friendThings[m]]
                    
        if len(results) == 0:
            return HttpResponse(json.dumps(results), mimetype='application/json')
            
        # Limit results to top 100
        results = dict(sorted(results.iteritems(), key=lambda x: x[1][0], reverse=True)[0:100])
        
        # Construct query of all resulting things
        categoryQuery = ''
        for m in results:
            categoryQuery += results[m][1] + ','
        
        # Add picture and link to resulting things
        categoryData = fb_call('?ids=' + categoryQuery[:-1], args={'fields': 'name, picture, link', 'access_token': access_token})
        for m in categoryData:
            if results.has_key(categoryData[m]['name']):
                results[categoryData[m]['name']].extend(
                    [categoryData[m]['picture'] if categoryData[m].has_key('picture') else question_mark_picture, categoryData[m]['link']])
        
        # Add unknown picture and link
        for x in results:
            if len(results[x]) <= 2:
                results[x].extend([question_mark_picture, ''])
        
        results = sorted(results.iteritems(), key=lambda x: x[1][0], reverse=True)
        
        return HttpResponse(json.dumps(results), mimetype='application/json')
