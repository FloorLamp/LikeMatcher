from django.db import models

class FBUser(models.Model):
    user_id = models.CharField(primary_key=True, max_length=50)
    me_data = models.TextField()
    friends_data = models.TextField()
    music_data = models.TextField()
    recommended_list = models.TextField()
    friends_list = models.TextField()
    
    def __unicode__(self):
        return self.user_id
