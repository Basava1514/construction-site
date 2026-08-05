from django.db import models

class Testimonial(models.Model):
    name = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    message = models.TextField()

    def __str__(self):
        return f"{self.name[:30]}"