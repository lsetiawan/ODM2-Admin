from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.db.models import Sum, Avg
from django.shortcuts import render_to_response
#from odm2testapp.forms import VariablesForm
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Measurementresultvalues
from .models import Profileresultvalues
from .models import Dataloggerfiles
from .models import Dataloggerfilecolumns
from .models import Featureactions
from .models import Samplingfeatures
from .models import Variables
from .models import Units
from .models import Results
from .models import Actions
from .models import Relatedfeatures
from .models import Profileresults
from datetime import datetime
import csv
import time
import datetime
from datetime import timedelta
from django.db.models import Q
from django.views.generic import ListView
import csv
import io
import binascii
import unicodedata
from io import TextIOWrapper
import cStringIO as StringIO
from templatesAndSettings.settings import MEDIA_ROOT
import itertools
from django.core.exceptions import ValidationError
from daterange_filter.filter import DateRangeFilter
from django import template
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.views.generic import View
from django.template import RequestContext
from .forms import DataloggerfilesAdmin
from .forms import DataloggerfilesAdminForm
from templatesAndSettings.settings import CUSTOM_TEMPLATE_PATH
register = template.Library()



def AddSensor(request):
    if request.user.is_authenticated():
        context = {'prefixpath': CUSTOM_TEMPLATE_PATH}
        return TemplateResponse(request, 'AddSensor.html', context)
    else:
        return HttpResponseRedirect('../')

def chartIndex(request):
    if request.user.is_authenticated():
        context = {'prefixpath': CUSTOM_TEMPLATE_PATH}
        return TemplateResponse(request, 'chartIndex.html', context)
    else:
        return HttpResponseRedirect('../')

#chartIndex
def AddProfile(request):
    if request.user.is_authenticated():
        context = {'prefixpath': CUSTOM_TEMPLATE_PATH}
        return TemplateResponse(request, 'AddProfile.html', context)
    else:
        return HttpResponseRedirect('../')

def RecordAction(request):
    if request.user.is_authenticated():
        context = {'prefixpath': CUSTOM_TEMPLATE_PATH}
        return TemplateResponse(request, 'RecordAction.html', context)
    else:
        return HttpResponseRedirect('../')


def ManageCitations(request):
    if request.user.is_authenticated():
        context = {'prefixpath': CUSTOM_TEMPLATE_PATH}
        return TemplateResponse(request, 'ManageCitations.html', context)
    else:
        return HttpResponseRedirect('../')
# #
# def dataloggerfilesView(request, id):
#      #model = Dataloggerfiles
#      #template_name = 'admin/odm2testapp/dataloggerfiles/change_form.html'#'DataloggerfilecolumnsDisplay.html'
#      DataloggerfilecolumnsList = Dataloggerfilecolumns.objects.filter(dataloggerfileid=id)
#      DataloggerfilecolumnsListvalues =  str(DataloggerfilecolumnsList.values())
#      #raise ValidationError(DataloggerfilecolumnsListvalues)
#      DataloggerfilecolumnsListvalues= DataloggerfilecolumnsList#DataloggerfilecolumnsListvalues.split('\'')
#      #request.session["DataloggerfilecolumnsList"] =DataloggerfilecolumnsListvalues
#      #fieldsets = Dataloggerfiles.objects.filter(dataloggerfileid=id)
#      adm = DataloggerfilesAdmin(Dataloggerfiles,admin) #.change_form_template
#      admform = DataloggerfilesAdminForm(request.POST)
#      #data =request.POST
#      data = {
#           'opts': Dataloggerfiles._meta,
#           'adminform': admform.formset,
#           'change': True,
#           'is_popup': False,
#           'to_field' : True,
#           'save_as': False,
#           #'prepopulated_fields' : adm.get_prepopulated_fields(request),
#           'has_delete_permission': True,
#           'has_add_permission': True,
#           'has_change_permission': True,
#           'DataloggerfilecolumnsList' : DataloggerfilecolumnsListvalues,}
# #
# # #DataloggerfilecolumnsDisplay.html
#      return render_to_response('admin/odm2testapp/dataloggerfiles/change_form.html', data, context_instance=RequestContext(request)) # DataloggerfilecolumnsDisplay.html

    # def get_context_data(self, **kwargs):
    #     context = super(dataloggercolumnView, self).get_context_data(**kwargs)
    #
    #     data = {'test': 'test',
    #     'opts': Dataloggerfiles._meta,
    #     'change': True,
    #     'is_popup': False,
    #     'save_as': False,
    #     'has_delete_permission': False,
    #     'has_add_permission': False,
    #     'has_change_permission': False}
    #     context['data'] = data
    #     context['DataloggerfilecolumnsList'] = Dataloggerfilecolumns.objects.all()
    #     return context
#register.inclusion_tag('DataloggerfilecolumnsDisplay.html')(dataloggercolumnView)

def get_name_of_sampling_feature(selected_result):

     title_feature_action = Featureactions.objects.filter(featureactionid=selected_result.values('featureactionid'))
     title_sampling_feature = Samplingfeatures.objects.filter(samplingfeatureid=title_feature_action.values('samplingfeatureid'))
     s = str(title_sampling_feature.values_list('samplingfeaturename',flat=True))
     name_of_sampling_feature= s.split('\'')[1]
     return name_of_sampling_feature

def get_name_of_variable(selected_result):
     title_variables = Variables.objects.filter(variableid=selected_result.values('variable'))
     s = str(title_variables.values_list('variablecode',flat=True))
     name_of_variable= s.split('\'')[1]
     return name_of_variable

def get_name_of_units(selected_result):
     title_units = Units.objects.filter(unitsid=selected_result.values('unitsid'))
     s = str(title_units.values_list('unitsname',flat=True))
     name_of_units= s.split('\'')[1]
     return name_of_units


def relatedFeaturesFilter(request,done,selected_relatedfeatid,selected_resultid,resultType='Temporal observation'):
    #selected_relatedfeatid = 18
    if 'SelectedRelatedFeature' in request.POST and not 'update_result_list' in request.POST:
        if not request.POST['SelectedRelatedFeature'] == 'All':
            done=True
            selected_relatedfeatid= int(request.POST['SelectedRelatedFeature'])
            relatedFeatureList = Relatedfeatures.objects.filter(relatedfeatureid=int(selected_relatedfeatid)).distinct('relatedfeatureid')
            relatedFeatureListLong = Relatedfeatures.objects.filter(relatedfeatureid=int(selected_relatedfeatid))#.select_related('samplingfeatureid','relationshiptypecv','relatedfeatureid')
            samplingfeatids= relatedFeatureListLong.values_list('samplingfeatureid', flat=True)
            resultList = Results.objects.filter(featureactionid__in=Featureactions.objects.filter(samplingfeatureid__in=samplingfeatids))#.select_related('variable','feature_action')
            if 'update_result_on_related_feature' in request.POST:
                #raise ValidationError(relatedFeatureList)
                selected_relatedfeatid= relatedFeatureList[0].relatedfeatureid.samplingfeatureid
                selected_resultid= resultList[0].resultid
        else:
            selected_relatedfeatid= request.POST['SelectedRelatedFeature']
            resultList = Results.objects.filter(result_type=resultType)[:25] # remove slice just for testing
    else:
        selected_relatedfeatid='All'
        resultList = Results.objects.filter(result_type=resultType)[:25]# remove slice just for testing
    return selected_relatedfeatid, done, resultList,selected_resultid




def temp_pivot_chart_view(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('../')

    selected_resultid = 15
    selected_featureactionid = 5
    selected_relatedfeatid = 18

    #relatedfeatureList
    #update_result_on_related_feature
    done=False
    selected_relatedfeatid, done, resultList,selected_resultid = relatedFeaturesFilter(request, done,selected_relatedfeatid,selected_resultid)

    if 'SelectedFeatureAction' in request.POST and not done:
        #raise ValidationError(done)
        if not request.POST['SelectedFeatureAction'] == 'All':
            selected_featureactionid= int(request.POST['SelectedFeatureAction'])
            resultList = Results.objects.filter(featureactionid=selected_featureactionid)
            if 'update_result_list' in request.POST:
                selected_resultid= resultList[0].resultid
        else:
            selected_featureactionid= request.POST['SelectedFeatureAction']
            resultList = Results.objects.filter(result_type="Temporal observation")
    elif not done:
        resultList = Results.objects.filter(featureactionid=selected_featureactionid)



    #find the measurement results series that where selected.
    numresults = resultList.count()
    selectedMResultSeries = []
    selectionStr = ''
    for i in range(0,numresults):
        selectionStr = str('selection' + str(i))
        if selectionStr in request.POST:
            #raise ValidationError(request.POST[selectionStr])
            for result in resultList:
                if int(request.POST[selectionStr]) == result.resultid:
                    selectedMResultSeries.append(int(request.POST[selectionStr]))
    #if 'selection0' in request.POST:
        #raise ValidationError(request.POST['selection0'] + ' '+ request.POST['selection1'])
        #selected_resultid = request.POST['selection0']
    #else:
        #selected_resultid = 15
    #if no series were selected (like on first load) set the series to some value.
    if len(resultList) > 0 and len(selectedMResultSeries)==0:
        selectedMResultSeries.append(int(resultList[0].resultid))
    elif len(resultList) == 0 and len(selectedMResultSeries)==0:
        selectedMResultSeries.append(15)


    if 'startDate' in request.POST:
        entered_start_date = request.POST['startDate']
    else:
        entered_start_date = "2015-07-20"
    if 'endDate' in request.POST:
        entered_end_date = request.POST['endDate']
    else:
        entered_end_date = "2015-07-21"
    if entered_end_date =='':
        entered_end_date = "2015-07-21"
    if entered_start_date=='':
        entered_start_date = "2015-07-20"

    selected_results = []
    name_of_sampling_features = []
    name_of_variables = []
    name_of_units = []
    myresultSeries = []
    i = 0
    data = {}


    for selectedMResult in selectedMResultSeries:
        i +=1
        selected_result = Results.objects.filter(resultid=selectedMResult)
        selected_results.append(selected_result)
        #name_of_sampling_features.append(get_name_of_sampling_feature(selected_result))

        tmpname = get_name_of_sampling_feature(selected_result)
        # if name_of_sampling_features.__len__() >0:
        #     namefound=False
        #     for name in name_of_sampling_features:
        #         if name == tmpname:
        #             namefound=True
        #     if not namefound:
        #         name_of_sampling_features.append(tmpname)
        #     else:
        #         name_of_sampling_features.append('')
        # else:
        name_of_sampling_features.append(tmpname)


        tmpname = get_name_of_variable(selected_result)
        if name_of_variables.__len__() >0:
            namefound=False
            for name in name_of_variables:
                if name == tmpname:
                    namefound=True
            if not namefound:
                 name_of_variables.append(tmpname)
            else:
                 name_of_variables.append('')
        else:
              name_of_variables.append(tmpname)

        tmpname = get_name_of_units(selected_result)
        if name_of_units.__len__() >0:
            namefound=False
            for name in name_of_units:
                if name == tmpname:
                    namefound=True
            if not namefound:
                name_of_units.append(tmpname)
            else:
                name_of_units.append('')
        else:
             name_of_units.append(tmpname)

        myresultSeries.append(Measurementresultvalues.objects.all().filter(~Q(datavalue=-6999))\
        .filter(~Q(datavalue=-888.88)).filter(valuedatetime__gt= entered_start_date)\
        .filter(valuedatetime__lt = entered_end_date)\
                    .filter(resultid=selectedMResult).order_by('-valuedatetime'))
        data.update({'datavalue' + str(i): []})

    # [Date.UTC(1971, 5, 10), 0]
    #{'data': [[1437435900, 71.47], [1437435000, 71.47],
     # [{
     #        data: [
     #            [Date.UTC(1970, 9, 21), 0],
     #            [Date.UTC(1970, 10, 4), 0.28],
    i = 0

    for myresults in myresultSeries:
        i+=1
        for result in myresults:
            start = datetime.datetime(1970,1,1)
            delta = result.valuedatetime-start
            mills = delta.total_seconds()*1000
            data['datavalue' + str(i)].append([mills, result.datavalue]) #dumptoMillis(result.valuedatetime)
            #data['datavalue'].extend(tmplist )
            #data['valuedatetime'].append(dumptoMillis(result.valuedatetime))


    #build strings for graph labels
    i = 0
    seriesStr = ''
    series = []
    titleStr = ''
    tmpUnit = ''
    tmpVariableName = ''
    tmpLocName= ''
    for name_of_unit,name_of_sampling_feature,name_of_variable in zip(name_of_units,name_of_sampling_features,name_of_variables) :
        i+=1
        if i==1 and not name_of_unit == '':
            seriesStr +=name_of_unit
        elif not name_of_unit == '':
                tmpUnit = name_of_unit
                seriesStr+=' - '+name_of_unit
        if not name_of_variable=='':
            tmpVariableName = name_of_variable
        if not name_of_unit == '':
            tmpUnit = name_of_unit
        if not name_of_sampling_feature =='':
            tmpLocName = name_of_sampling_feature
        series.append({"name": tmpUnit +' - '+ tmpVariableName +' - '+ tmpLocName,"yAxis": tmpUnit, "data": data['datavalue'+str(i)]})
    i=0
    for name_of_sampling_feature,name_of_variable in zip(name_of_sampling_features,name_of_variables) :
        i+=1
        if i ==1:
            titleStr += name_of_sampling_feature  #+ ', ' +name_of_variable
        else:
            titleStr += ' - '  +name_of_sampling_feature #+name_of_variable+ ', '

    chartID = 'chart_id'
    chart = {"renderTo": chartID, "type": 'scatter',  "zoomType": 'xy',}
    title2 = {"text": titleStr}
    xAxis = {"type": 'datetime', "title": {"text": 'Date'},}
    yAxis = {"title": {"text": seriesStr}}
    graphType = 'line'
    opposite = False


    actionList = Actions.objects.filter(action_type="Observation") #where the action is not of type estimation
    #assuming an estimate is a single value.
    featureactionList = Featureactions.objects.filter(action__in=actionList)
    relatedFeatureList = Relatedfeatures.objects.order_by('relatedfeatureid').distinct('relatedfeatureid')
    int_selectedresultid_ids = []
    for int_selectedresultid in selectedMResultSeries:
        int_selectedresultid_ids.append(int(int_selectedresultid))
    csvexport = False
    #if the user hit the export csv button export the measurement results to csv
    if request.REQUEST.get('export_data'):
        csvexport=True

        myfile = StringIO.StringIO()
        for myresults in myresultSeries:
            for result in myresults:
                myfile.write(result.csvoutput())
            myfile.write('\n')
        response = HttpResponse(myfile.getvalue(),content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="mydata.csv"'
    if csvexport:
        return response
    else:
        #raise ValidationError(relatedFeatureList)
        return TemplateResponse(request,'chart.html',{ 'featureactionList': featureactionList,'prefixpath': CUSTOM_TEMPLATE_PATH, 'resultList': resultList,
            'startDate':entered_start_date,'endDate':entered_end_date, 'SelectedResults':int_selectedresultid_ids,
             'chartID': chartID, 'chart': chart,'series': series, 'title2': title2, 'graphType':graphType, 'xAxis': xAxis, 'yAxis': yAxis,'name_of_units':name_of_units,
            'relatedFeatureList': relatedFeatureList,'SelectedRelatedFeature':selected_relatedfeatid, 'SelectedFeatureAction':selected_featureactionid,},)
#
# #maybe don't need this
# def relatedFeaturesFilterForVariables(request,done,selected_relatedfeatid,selected_variableid,resultType='Temporal observation'):
#     #selected_relatedfeatid = 18
#     if 'SelectedRelatedFeature' in request.POST:
#         if not request.POST['SelectedRelatedFeature'] == 'All':
#             done=True
#             selected_relatedfeatid= int(request.POST['SelectedRelatedFeature'])
#             relatedFeatureList = Relatedfeatures.objects.filter(relatedfeatureid=int(selected_relatedfeatid)).distinct('relatedfeatureid')
#             relatedFeatureListLong = Relatedfeatures.objects.filter(relatedfeatureid=int(selected_relatedfeatid))#.select_related('samplingfeatureid','relationshiptypecv','relatedfeatureid')
#             samplingfeatids= relatedFeatureListLong.values_list('samplingfeatureid', flat=True)
#             variableList = Variables.objects.filter(featureactionid__in=Featureactions.objects.filter(sampling_feature__in=samplingfeatids))#.select_related('variable','feature_action')
#             if 'update_result_on_related_feature' in request.POST:
#                 #raise ValidationError(relatedFeatureList)
#                 selected_relatedfeatid= relatedFeatureList[0].relatedfeatureid.samplingfeatureid
#         else:
#             selected_relatedfeatid= request.POST['SelectedRelatedFeature']
#     else:
#         selected_relatedfeatid='All'
#     return selected_relatedfeatid, done, variableList

def graph_data(request):
    #if not request.user.is_authenticated():
        #return HttpResponseRedirect('../')

    selected_resultid = 9365
    selected_relatedfeatid = 15

    #relatedfeatureList
    #update_result_on_related_feature
    done=False

    #need a variables list instead of a results list
    # find the variables for the selected related feature

    if 'SelectedRelatedFeature' in request.POST:
        if not request.POST['SelectedRelatedFeature'] == 'All':
            #relatedFeature = Samplingfeatures.objects.filter(samplingfeatureid=selected_relatedfeatid) #Relatedfeatures.objects.filter(relatedfeatureid=int(selected_relatedfeatid)).distinct('relatedfeatureid')
            selected_relatedfeatid = int(request.POST['SelectedRelatedFeature'])
        else:
            selected_relatedfeatid = 15
            #relatedFeature = Samplingfeatures.objects.filter(samplingfeatureid=selected_relatedfeatid)

    else:
        selected_relatedfeatid = 15
    #find variables found at the sampling feature
    #need to go through featureaction to get to results
    variableList = None
    #need the feature actions for all of the sampling features related to this sampling feature
    sampling_features = Relatedfeatures.objects.filter(relatedfeatureid=selected_relatedfeatid)
    #select the feature actions for all of the related features.
    feature_actions = Featureactions.objects.filter(samplingfeatureid__in = sampling_features)
    featureresults = Results.objects.filter(featureactionid__in=feature_actions)
    variableList = Variables.objects.filter(variableid__in =featureresults.values("variable"))

    #find the profile results series for the selected variable
    numvariables = variableList.__len__()
    #raise ValidationError(numvariables)
    selectedMVariableSeries = []
    selectionStr = ''
    for i in range(0,numvariables):
        selectionStr = str('selection' + str(i))
        if selectionStr in request.POST:
            #raise ValidationError(request.POST[selectionStr])
            for variable in variableList:
                if int(request.POST[selectionStr]) == variable.variableid:
                    selectedMVariableSeries.append(int(request.POST[selectionStr]))

    #if no series were selected (like on first load) set the series to some value.
    if len(variableList) > 0 and len(selectedMVariableSeries)==0:
        selectedMVariableSeries.append(int(variableList[0].variableid))
    elif len(variableList) == 0 and len(selectedMVariableSeries)==0:
        selectedMVariableSeries.append(15)

    selectedMResultsSeries = None
    for variable in selectedMVariableSeries:
        if not selectedMResultsSeries:
            selectedMResultsSeries = featureresults.filter(variable_id=variable)
        else: #concatenante the sets of results for each variable
            selectedMResultsSeries = selectedMResultsSeries | featureresults.filter(variable_id=variable)
            #if 'SelectedFeatureAction' in request.POST:
                #raise ValidationError(selectedMResultsSeries)
    selected_results = []
    name_of_sampling_features = []
    name_of_variables = []
    name_of_units = []
    unitAndVariable = ''
    myresultSeries = []
    tmpUnit = ''
    tmpVariableName = ''
    lastUnitAndVariable = ''
    tmpLocName= ''
    i = 0
    data = {}
    data2= []
    resultValuesSeries = None
    #if 'update_result_on_related_feature' in request.POST:
            #raise ValidationError(selectedMResultsSeries)
    for selectedMResult in selectedMResultsSeries:
        i +=1
        selected_result = Results.objects.filter(resultid=selectedMResult.resultid)
        #if 'update_result_on_related_feature' in request.POST:
            #raise ValidationError(selected_result)
        selected_results.append(selected_result)
        #name_of_sampling_features.append(get_name_of_sampling_feature(selected_result))

        tmpname = get_name_of_sampling_feature(selected_result)
        tmpLocName = tmpname



        tmpname = get_name_of_variable(selected_result)
        unitAndVariable = tmpname
        tmpVariableName = tmpname
        if name_of_variables.__len__() >0:
            namefound=False
            for name in name_of_variables:
                if name == tmpname:
                    namefound=True
            if not namefound:
                 name_of_variables.append(tmpname)
            else:
                 name_of_variables.append('')
        else:
              name_of_variables.append(tmpname)

        tmpname = get_name_of_units(selected_result)
        tmpUnit = tmpname
        unitAndVariable = unitAndVariable + " " + tmpname
        if name_of_units.__len__() >0:
            namefound=False
            for name in name_of_units:
                if name == tmpname:
                    namefound=True
            if not namefound:
                name_of_units.append(tmpname)
            else:
                name_of_units.append('')
        else:
             name_of_units.append(tmpname)

        resultValues= Profileresultvalues.objects.all().filter(~Q(datavalue=-6999))\
        .filter(~Q(datavalue=-888.88)).filter(resultid=selectedMResult)
        if not resultValuesSeries:
            resultValuesSeries = resultValues
        else:
            resultValuesSeries = resultValuesSeries | resultValues
        #if 'update_result_on_related_feature' in request.POST:
            #raise ValidationError(resultValues)
        for resultValue in resultValues:
            seriesName = 'datavalue' + unitAndVariable
            tmpLocName = tmpLocName + " Depth " + str(resultValue.zlocation) + " " + str(resultValue.zlocationunitsid.unitsabbreviation)
            name_of_sampling_features.append(tmpLocName)
            if seriesName in data:
                data['datavalue' + unitAndVariable].append([ tmpLocName,resultValue.datavalue]) #tmpUnit +' - '+tmpVariableName +' - '+
            else:
                data.update({'datavalue' + unitAndVariable: []})
                data['datavalue' + unitAndVariable].append([tmpLocName,resultValue.datavalue]) #tmpUnit +' - '+tmpVariableName +' - '+
            #data['datavalue' + unitAndVariable].append( resultValue.datavalue) #get_name_of_variable(selected_result) + " " + get_name_of_sampling_feature(selected_result) ,
            #data2.append(resultValue.datavalue)

    #build strings for graph labels
    i = 0
    seriesStr = ''
    series = []
    titleStr = ''
    tmpUnit = ''
    tmpVariableName = ''
    lastUnitAndVariable = ''
    tmpLocName= ''
    #xAxisCategories = []
    for name_of_unit,name_of_sampling_feature,name_of_variable in zip(name_of_units,name_of_sampling_features,name_of_variables) :
        i+=1
        if i==1 and not name_of_unit == '':
            seriesStr +=name_of_unit
        elif not name_of_unit == '':
                tmpUnit = name_of_unit
                seriesStr+=' - '+name_of_unit
        if not name_of_variable=='':
            tmpVariableName = name_of_variable
        if not name_of_unit == '':
            tmpUnit = name_of_unit
        if not name_of_sampling_feature =='':
            tmpLocName = name_of_sampling_feature
        lastUnitAndVariable = unitAndVariable
        unitAndVariable = tmpVariableName + " " + tmpUnit
        #xAxisCategories.append(tmpUnit + ' ' + tmpVariableName +' - '+ tmpLocName)
        if lastUnitAndVariable != unitAndVariable:
            series.append({"name":tmpUnit +' - '+tmpVariableName,"yAxis": tmpUnit, "data": data['datavalue'+unitAndVariable]}) #removewd from name +' - '+ tmpLocName
        #series.append(data['datavalue'+str(i)])

    i=0
    for name_of_sampling_feature,name_of_variable in zip(name_of_sampling_features,name_of_variables) :
        i+=1
        if i ==1:
            titleStr += name_of_variable  #+ ', ' +name_of_sampling_feature
        else:
            titleStr += ' - '  +name_of_variable #+name_of_sampling_feature+ ', '
    #series = series.append({})
    chartID = 'chart_id'
    chart = {"renderTo": chartID, "type": 'column',  "zoomType": 'xy',}
    title2 = {"text": titleStr}
    #xAxis = {"categories":xAxisCategories,} #"type": 'category',"title": {"text": xAxisCategories},
    yAxis = {"title": {"text": seriesStr}}
    graphType = 'column'
    opposite = False

    withProfileResults = Profileresults.objects.all()
    results = Results.objects.filter(resultid__in=withProfileResults)
    featureAction = Featureactions.objects.filter(featureactionid__in=results.values("featureactionid"))
    relatedFeatureList = Relatedfeatures.objects.filter(samplingfeatureid__in=featureAction).order_by('relatedfeatureid').distinct('relatedfeatureid')
    #raise ValidationError(list(featureAction.values("samplingfeatureid")))
    #raise ValidationError(list(results.values("resultid")))
    #
    # withProfileResults = Profileresults.objects.all()
    # resultswithProfile = Results.objects.filter(resultid__in=withProfileResults)
    # #featureaction has featureactionid, samplingfeatureid, actionid
    # featureAction = Featureactions.objects.filter(featureactionid__in=resultswithProfile)
    # relatedFeatureList = Relatedfeatures.objects.filter(samplingfeatureid__in=featureAction.values('samplingfeatureid')).order_by('relatedfeatureid').distinct('relatedfeatureid')
    # relatedFeatureList = Relatedfeatures.objects.all()
    # results = Results.objects.filter(samplingfeatureid__in=relatedFeatureList.values('samplingfeatureid'))
    # withProfileResults = Profileresults.objects.filter(resultid__in=results)

    #relatedFeatureList = Relatedfeatures.objects.filter().order_by('relatedfeatureid').distinct('relatedfeatureid')
    #raise ValidationError(list(featureAction))
    #relatedFeatureList = None
    #for profileResult in withProfileResults:
    #     result = Results.objects.filter(resultid=profileResult.resultid.resultid)
    #     featureAction = Featureactions.objects.filter(featureactionid=result[0].featureactionid.featureactionid)
    #     if relatedFeatureList:
    #         relatedFeatureList = relatedFeatureList | Relatedfeatures.objects.get(samplingfeatureid=
    #                         featureAction.values("samplingfeatureid"))

    #     else:
    #         relatedFeatureList = Relatedfeatures.objects.get(samplingfeatureid=
    #                         featureAction.values("samplingfeatureid"))

    int_selectedvariable_ids = []
    for int_selectedvariableid in selectedMVariableSeries:
        int_selectedvariable_ids.append(int(int_selectedvariableid))
    csvexport = False
    #if the user hit the export csv button export the measurement results to csv
    if request.REQUEST.get('export_data'):
        csvexport=True

        myfile = StringIO.StringIO()
        #raise ValidationError(resultValues)
        for myresults in resultValuesSeries:
        #for myresults in profileresult:
            myfile.write(myresults.csvoutput())
            myfile.write('\n')
        response = HttpResponse(myfile.getvalue(),content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="mydata.csv"'
    if csvexport:
        return response
    else:
        #raise ValidationError(relatedFeatureList)
        return TemplateResponse(request,'chartVariableAndFeature.html',{'prefixpath': CUSTOM_TEMPLATE_PATH,  'variableList': variableList,
             'SelectedVariables':int_selectedvariable_ids,
             'chartID': chartID, 'chart': chart,'series': series, 'title2': title2, 'graphType':graphType, 'yAxis': yAxis,'name_of_units':name_of_units,
            'relatedFeatureList': relatedFeatureList,'SelectedRelatedFeature':selected_relatedfeatid,},)


#
# def ManageCitations(request):
#     if request.user.is_authenticated():
#         context = {'prefixpath': CUSTOM_TEMPLATE_PATH}
#         return TemplateResponse(request, 'ManageCitations.html', context)
#     else:
#         return HttpResponseRedirect('../')