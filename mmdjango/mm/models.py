from django.db import models

class FBUser(models.Model):
    user_id = models.CharField(primary_key=True, max_length=50)
    me_data = models.TextField()
    
    music_data = models.TextField()
    music_friend_data = models.TextField()
    music_recommended_data = models.TextField()
    music_friendslist_data = models.TextField()
    
    movies_data = models.TextField()
    movies_friend_data = models.TextField()
    movies_recommended_data = models.TextField()
    movies_friendslist_data = models.TextField()
    
    tv_data = models.TextField()
    tv_friend_data = models.TextField()
    tv_recommended_data = models.TextField()
    tv_friendslist_data = models.TextField()
    
    books_data = models.TextField()
    books_friend_data = models.TextField()
    books_recommended_data = models.TextField()
    books_friendslist_data = models.TextField()
    
    games_data = models.TextField()
    games_friend_data = models.TextField()
    games_recommended_data = models.TextField()
    games_friendslist_data = models.TextField()
    
    interests_data = models.TextField()
    interests_friend_data = models.TextField()
    interests_recommended_data = models.TextField()
    interests_friendslist_data = models.TextField()
    
    activities_data = models.TextField()
    activities_friend_data = models.TextField()
    activities_recommended_data = models.TextField()
    activities_friendslist_data = models.TextField()
    
    likes_data = models.TextField()
    likes_friend_data = models.TextField()
    likes_recommended_data = models.TextField()
    likes_friendslist_data = models.TextField()
    
    def __unicode__(self):
        return self.user_id
