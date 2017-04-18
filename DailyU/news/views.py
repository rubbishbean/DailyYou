from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from .models import Category, User
from el_pagination.views import AjaxListView
from el_pagination.decorators import page_template
from .webhoseUtil import WebhoseUtil
from .twi_util import *
from . import word_util
from textblob import TextBlob as tb
import os
import sys


# Create your views here.

# The index page is not allow to any view without authentication
def getCurrentUser(request):
    username = request.session.get('current_user',None)
    if username is not None:
        user = User.objects.get(username =username )
    else:
        user = None
    return user

def check_login(orig_func):
    def temp_func(request):
        if getCurrentUser(request) == None:
            return HttpResponseRedirect("/login")
        else:
            return orig_func(request)
    return temp_func


@check_login
def index(request):
    username = request.session.get('current_user',None)
    user = User.objects.get(username=username)
    print(username)
    u = User.objects.get(username="yaling")
    u.addCateToUser('sports')
    print('***************test dbutils***************\n'+','.join(u.getUserCates()))
    u.rmCateFromUser('sports')
    output = ','.join(u.getUserCates())
    return render(request,"home.html",{'user':user,'categories':user.getUserCates()})

def login(request):
    username = request.POST.get('username',False)
    password = request.POST.get('password',False)
    try:
        user = User.objects.get(username=username)
        if(str(user.password) == str(password)):
            request.session['current_user'] = user.username
            return HttpResponseRedirect("/")
        else:
            return render(request,"login.html",{'err':'login error','user':None})
    except:
        e = sys.exc_info()[0]
        print(e)
    return render(request, "login.html")

def logout(request):
    del request.session['current_user']
    return HttpResponseRedirect("/login")


def editCategory(request):
    username = request.session.get('current_user',None)
    user = User.objects.get(username=username)
    if 'add_cat' in request.POST:
        new_category_name = request.POST.get('new_cat',False)
        if len(Category.objects.filter(cate_name=new_category_name)) != 0:
            #new_category = Category.objects.create(cate_name=new_category_name)
            if not new_category_name in user.getUserCates():
                user.addCateToUser(new_category_name)
        return HttpResponseRedirect("/")
        
    elif 'delete_cat' in request.POST:
        delete_cat_name = request.POST.get('current_cate',False)
        print(delete_cat_name)
        user.rmCateFromUser(delete_cat_name)
        return HttpResponseRedirect("/")



    return render(request, "home.html")

def downloadPDF(request):
    return HttpResponse("download pdf page")

def newspaperIndex(request):
    cur_user = getCurrentUser(request)
    sections = cur_user.getUserCates()
    sup_sections = []
    wh = WebhoseUtil()
    for s in sections:
        '''For development purpose, load existing json'''
        #wh.request(s)
        file_path = os.path.join(os.path.dirname(__file__), 'test_jsons/'+s+'.json')
        #wh.saveToFile(file_path)
        wh.loadJson(file_path)
        text = ""
        for i in range(min(10,wh.numOfPosts())):
            title = wh.getTitle(i)
            text = text+str(i+1)+". "+title+"\n"
        text = text+"More to be explored..."
        sup_sections.append({"name":s,"text":text})
    return render(request, "sections.html", {'sections':sup_sections})

@page_template('post_list_page.html')
def generateNewspaper(request,section_name,extra_context=None):
    cur_user = getCurrentUser(request)
    sections = cur_user.getUserCates()
    wh = WebhoseUtil()
    '''For development purpose, load existing json'''
    #wh.request(section_name)
    file_path = os.path.join(os.path.dirname(__file__), 'test_jsons/'+section_name+'.json')
    wh.loadJson(file_path)
    posts = []
    titles = []
    texts = []
    for i in range(wh.numOfPosts()):
        title = wh.getTitle(i)
        post_url = wh.getUrl(i)
        img = wh.getImg(i)
        text = wh.getText(i)
        author = wh.getAuthor(i)
        pub_time = wh.getPubTime(i)
        titles.append(title)
        texts.append(tb(text))
        posts.append({"title": title,
                      "post_url": post_url,
                      "text": text,
                      "author": author,
                      "pub_time": pub_time,
                      "img" : img})

    tweets = getTweets(texts[:10],titles[:10])
    for i in range(10):
        posts[i]["tweets"] = tweets[i]
    
    context = {
        'posts': posts,
        'sections' : sections,
        'section_name':section_name,
        'page_template': page_template,
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, "post_list.html", context)

def getTweets(text_list,title_list):
    sorted_title_list= word_util._sort_words(text_list,title_list)
    tw = twi_util()
    tw.appAuth_api()
    tw_for_section = []
    for title in sorted_title_list:
        raw_tw =tw.get_all_related_tweets(title,100,100)
        filtered = list(tw.most_relevant(raw_tw,4))
        tw_for_section.append(filtered)
    return tw_for_section



