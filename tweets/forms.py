from django import forms
from .models import Tweet


class TweetForm(forms.ModelForm):
    MAX_TWEET_LENGTH = 240

    class Meta:
        model = Tweet
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data.get("content")
        if len(content) > self.MAX_TWEET_LENGTH:
            raise forms.ValidationError("This tweet is too long")
        return content
