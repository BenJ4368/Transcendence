from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static

#blank = True allows to left form fields empty
#null=True allows to left value null


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)#if the user is deleted, the profile will be deleted too
	image = models.ImageField(upload_to='avatars', null=True, blank=True)#images will be stored "media/avatars"
	displayname = models.CharField(max_length=20, null=True, blank=True)
	info = models.TextField(null=True, blank=True)

	friends = models.ManyToManyField('self', symmetrical=True, blank=True)
	pending_request = models.ManyToManyField('self', related_name='invite_request', symmetrical=False, blank=True)
	def __str__(self):
		return str(self.user)
	
	@property
	def name(self):
		if self.displayname:
			name = self.displayname
		else:
			name = self = self.user.username
		return name
	
	#try to download image url if fail put the default image
	@property
	def avatar(self):
		try:
			avatar = self.image.url
		except:
			avatar = static('images/avatar.svg')
		return avatar

class Relation(models.Model):
	status = models.BooleanField(default=False)
	requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requester")
	target = models.ForeignKey(User, on_delete=models.CASCADE, related_name="target")

	def __str__(self):
		return f"{self.requester.username} -> {self.target.username}"