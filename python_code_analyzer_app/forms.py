from django import forms

from .models import Repository, Analysis, AnalysisTool

class RepositoryForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = ['url']
        labels = {'url': 'Repository url'}

class AnalysisForm(forms.ModelForm):
    class Meta:
        model = Analysis
        fields = ['status']
        labels = {'status':'Status'}
        # widgets = {
        #     'herramientas':forms.CheckboxSelectMultiple()
        # }

    def __init__(self, *args, **kwargs): 
        super(AnalysisForm, self).__init__(*args, **kwargs)                       
        self.fields['status'].disabled = True

class AnalysisToolForm(forms.ModelForm):
    class Meta:
            model = AnalysisTool
            fields = ['tool']
            labels = {
                'tool':'Tool'
            }

    # def __init__(self, *args, **kwargs): 
    #     super(AnalysisToolForm, self).__init__(*args, **kwargs)                       
    #     self.fields['tool_id'].disabled = True
    #     self.fields['parameters'].disabled = True

class UploadFileForm(forms.Form):
    # title = forms.CharField(max_length=50)
    file = forms.FileField()