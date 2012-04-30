from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from mm.models import FBUser
import ast
import requests
import base64
import os
import os.path
import urllib
import hmac
import json
import hashlib
from base64 import urlsafe_b64decode, urlsafe_b64encode

FB_APP_ID = '274847765934546'
FB_APP_SECRET = '888949406beb1a60ce62963d679678f9'
FB_API_SCOPE = 'user_likes+friends_likes+read_friendlists+publish_stream'
SECRET_CODE = None
requests = requests.session()

app_url = 'https://graph.facebook.com/{0}'.format(FB_APP_ID)
FB_APP_NAME = json.loads(requests.get(app_url).content).get('name')
COOKIE_TOKEN = 'fbapp' + FB_APP_ID + 'token'
COOKIE_FBID = 'fbapp' + FB_APP_ID + 'fbid'
question_mark_picture = 'http://local2social.com/wp-content/uploads/2011/02/questionmark.jpg'

def oauth_login_url(request):
    fb_login_uri = ("https://www.facebook.com/dialog/oauth"
                    "?client_id=%s&redirect_uri=%s&scope=%s" %
                    (FB_APP_ID, get_code_url(request), FB_API_SCOPE))

    print "LOGIN URL: " + fb_login_uri
    return fb_login_uri


def simple_dict_serialisation(params):
    return "&".join(map(lambda k: "%s=%s" % (k, params[k]), params.keys()))


def base64_url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip('=')


def fbapi_get_string(path,
    domain=u'graph', params=None, access_token=None,
    encode_func=urllib.urlencode):
    """Make an API call"""

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

    result = fbapi_get_string(path=u"/oauth/access_token?", params=params,
                              encode_func=simple_dict_serialisation)
    print result
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

#def get_token(request):

#    if request.GET.get('code', None):
#        return fbapi_auth(request.GET.get('code'))[0]
#    else:
#	    return None

#    cookie_key = 'fbsr_{0}'.format(FB_APP_ID)
#    if cookie_key in request.session.keys():

#        c = request.session.get(cookie_key)
#        encoded_data = c.split('.', 2)

#        sig = encoded_data[0]
#        data = json.loads(urlsafe_b64decode(str(encoded_data[1]) + '=='))

#        if not data['algorithm'].upper() == 'HMAC-SHA256':
#            raise ValueError('unknown algorithm {0}'.format(data['algorithm']))

#        h = hmac.new(FB_APP_SECRET, digestmod=hashlib.sha256)
#        h.update(encoded_data[1])
#        expected_sig = urlsafe_b64encode(h.digest()).replace('=', '')

#        if sig != expected_sig:
#            raise ValueError('bad signature')

#        code =  data['code']

#        params = {
#            'client_id': FB_APP_ID,
#            'client_secret': FB_APP_SECRET,
#            'redirect_uri': '',
#            'code': data['code']
#        }

#        from urlparse import parse_qs
#        r = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
#        token = parse_qs(r.content).get('access_token')

#        return token

def fql(fql, token, args=None):
    if not args:
        args = {}

    args["query"], args["format"], args["access_token"] = fql, "json", token

    url = "https://api.facebook.com/method/fql.query"

    r = requests.get(url, params=args)
    return json.loads(r.content)

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

def index(request):
#    if not access_token:
#        get_token(request)

#    channel_url = url_for('get_channel', _external=True)
#    channel_url = channel_url.replace('http:', '').replace('https:', '')

    access_token = request.session.get(COOKIE_TOKEN, None)
    
    if access_token:
        # Only do facebook api search if user refreshes
        do_api_search = request.POST.get('refresh', False)
        
        me = {}
        friendsData = {}
        myMusicData = {}
        recommendedList = []
        friendsList = []
        user_id = request.session.get(COOKIE_FBID, None)
        
        if user_id:
            user = FBUser.objects.get(pk=user_id)
            if user:
                if not do_api_search:
                    me = ast.literal_eval(user.me_data)
                    friendsData = ast.literal_eval(user.friends_data)
                    myMusicData = ast.literal_eval(user.music_data)
                    recommendedList = ast.literal_eval(user.recommended_list)
                    friendsList = ast.literal_eval(user.friends_list)
                    haveMusic = (len(myMusicData['data']) > 0)
            else:
                do_api_search = True
        else:
            do_api_search = True
        
        if do_api_search:
            me = fb_call('me', args={'access_token': access_token})
            if not me:
                return redirect(get_home(request))
            friendsData = fb_call('me/friends', args={'fields': 'name,id,picture,music', 'access_token': access_token})        
            myMusicData = fb_call('me/music', args={'access_token': access_token}) # FB data for my musicData
            
            # Save cookie
            request.session[COOKIE_FBID] = me['id']
        
            myMusic = {} # List of my artists
            haveMusic = True # If I have artists
            recommended = {} # Dict of recommended music: {artist name: [rating, id]}
            friends = {} # Dict of friends: {friend id: [name, picture, common artists]}
        
            # Gets my list of music if I have any
            if len(myMusicData['data']) == 0:
                haveMusic = False
            else:
                for m in myMusicData['data']:
                    myMusic[m['name']] = m['id']
            
            for f in friendsData['data']:
                friends[f['id']] = [f['name'], f['picture']]
                
                # Skip empty music data
                if not f.get('music'):
                    friends[f['id']].append(None)
                    continue
                
                # Gets list of friend music
                friendMusic = {}
                for m in f['music']['data']:
                    friendMusic[m['name']] = m['id']
                    
                # Finds common artists between me and friend
                # Sets weight to 1 if I have no arists, or to the number of artists we have in common
                common = []
                weight = 1
                if haveMusic:
                    common = set(myMusic) & set(friendMusic)
                    weight = len(common)/float(len(friendMusic))
                friends[f['id']].extend([len(common), list(common)])
                
                # If we have artists in common or I have no artists,
                # then add all their artists to recommended list and increment rating by weight
                if len(common) > 0 or not haveMusic:
                    theirMusic = set(friendMusic) - set(myMusic)
                    for m in theirMusic:
                        recommended[m] = [recommended.get(m, [0])[0] + weight, friendMusic[m]]
                
            # Limit recommend to top 200
            recommended = dict(sorted(recommended.iteritems(), key=lambda x: x[1][0], reverse=True)[0:200])
            
            # Construct query of all recommended artists
            recommendedMusicQuery = ''
            for m in recommended:
                recommendedMusicQuery += recommended[m][1] + ','
            
            # Add picture and link to recommended artists
            musicData = fb_call('?ids=' + recommendedMusicQuery[:-1], args={'fields': 'name, picture, link', 'access_token': access_token})
            for m in musicData:
                recommended[musicData[m]['name']].extend(
                [musicData[m]['picture'] if musicData[m].has_key('picture') else question_mark_picture, musicData[m]['link']])
                
            # Add unknown picture and link
            for x in recommended:
                if len(recommended[x]) <= 2:
                    results[x].extend([question_mark_picture, ''])
                
            # Sort recommended artist list by rating
            recommendedList = sorted(recommended.iteritems(), key=lambda x: x[1][0], reverse=True)
            friendsList = sorted(friends.iteritems(), key=lambda x: x[1][2], reverse=True)
            
            # Save to database
            user = FBUser(pk=me['id'], me_data=me, friends_data=friendsData, music_data=myMusicData, recommended_list=recommendedList, friends_list=friendsList)
            user.save()

        return render_to_response('index.html', 
        {'app_id': FB_APP_ID, 'token': access_token, 'url': get_home(request), 'friendsList': friendsList, 'recommendedList': recommendedList[0:50], 'haveMusic': haveMusic, 'me': me, 'name': FB_APP_NAME})
    else:
        return redirect(oauth_login_url(request))

def get_channel():
    return render_to_response('channel.html')

def close():
    return render_to_response('close.html')

# API for searching friends for artist
def api(request):
    access_token = request.session.get(COOKIE_TOKEN, None)
    user_id = request.session.get(COOKIE_FBID, None)
    user = FBUser.objects.get(pk=user_id)
    searchArtist = request.GET.get('q', None)
    if request.method == 'GET' and searchArtist and user_id and user:# and request.is_ajax():
        friendsData = ast.literal_eval(user.friends_data)
        results = {}
        for f in friendsData['data']:
            # Skip empty music data
            if not f.get('music'):
                continue
            
            # Gets list of friend music
            friendMusic = {}
            for m in f['music']['data']:
                friendMusic[m['name']] = m['id']
            # Searches friends music for artist and adds to results
            if friendMusic.has_key(searchArtist):
                del friendMusic[searchArtist]
                for m in friendMusic:
                    results[m] = [results.get(m, [0])[0] + 1, friendMusic[m]]
                    
        if len(results) == 0:
            return HttpResponse(json.dumps(results), mimetype='application/json')
            
        # Limit results to top 100
        results = dict(sorted(results.iteritems(), key=lambda x: x[1][0], reverse=True)[0:100])
        
        # Construct query of all resulting artists
        musicQuery = ''
        for m in results:
            musicQuery += results[m][1] + ','
        
        # Add picture and link to resulting artists
        musicData = fb_call('?ids=' + musicQuery[:-1], args={'fields': 'name, picture, link', 'access_token': access_token})
        for m in musicData:
            if results.has_key(musicData[m]['name']):
                results[musicData[m]['name']].extend(
                    [musicData[m]['picture'] if musicData[m].has_key('picture') else question_mark_picture, musicData[m]['link']])
        
        # Add unknown picture and link
        for x in results:
            print results[x]
            if len(results[x]) <= 2:
                results[x].extend([question_mark_picture, ''])
        
        results = sorted(results.iteritems(), key=lambda x: x[1][0], reverse=True)
        
        return HttpResponse(json.dumps(results), mimetype='application/json')
