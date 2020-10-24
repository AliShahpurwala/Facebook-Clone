from django.http import HttpResponse,HttpResponseNotFound, JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from datetime import date
from . import models
import copy
def messages_view(request):
    """Private Page Only an Authorized User Can View, renders messages page
       Displays all posts and friends, also allows user to make new posts and like posts
    Parameters
    ---------
      request: (HttpRequest) - should contain an authorized user
    Returns
    --------
      out: (HttpResponse) - if user is authenticated, will render private.djhtml
    """
    if request.user.is_authenticated:
        user_info = models.UserInfo.objects.get(user=request.user)
        hold = user_info.interests.all()
        interests_list = []
        for i in hold:
            interests_list.append(str(i))

        # Creating a list of friends
        friendsList = []
        for fr in user_info.friends.all():
            friendsList.append(fr)



        # TODO Objective 9: query for posts (HINT only return posts needed to be displayed)
        posts = []
        posts = models.Post.objects.all().order_by('-timestamp')
        postObject = {'postContent': None, 'numLikes': 0, 'likedByCurrentUser': False}
        postObjectList = []
        for i in posts:
            postObject['postContent'] = i
            postObject['numLikes'] = len(i.likes.all())
            if user_info in i.likes.all():
                postObject['likedByCurrentUser'] = True
            copyObject = copy.deepcopy(postObject)
            postObjectList.append(copyObject)
            postObject['likedByCurrentUser'] = False
        
        
        # TODO Objective 10: check if user has like post, attach as a new attribute to each post

        context = { 'user_info' : user_info
                  , 'posts' : postObjectList[0:request.session['numPosts']]
                  , 'interests0':  interests_list
                  , 'friendsList': friendsList}
        return render(request,'messages.djhtml',context)

    request.session['failed'] = True
    return redirect('login:login_view')

def account_view(request):
    """Private Page Only an Authorized User Can View, allows user to update
       their account information (i.e UserInfo fields), including changing
       their password
    Parameters
    ---------
      request: (HttpRequest) should be either a GET or POST
    Returns
    --------
      out: (HttpResponse)
                 GET - if user is authenticated, will render account.djhtml
                 POST - handle form submissions for changing password, or User Info
                        (if handled in this view)
    """
    if request.user.is_authenticated:
        # TODO Objective 3: Create Forms and Handle POST to Update UserInfo / Password
        form = None
        user_info = models.UserInfo.objects.get(user=request.user)
        interests_list = []
        if 'updateInfo' in request.POST:
            if request.method == 'POST':
                interests_list = []
                context = request.POST
                newEmployment = context['changeEmployment']
                if newEmployment != '':
                    user_info.employment = newEmployment
                    user_info.save()
                newLocation = context['changeLocation']
                if newLocation != '':
                    user_info.location = newLocation
                    user_info.save()
                newYear = context['changeYear']
                newMonth = context['changeMonth']
                newDay = context['changeDay']
                checkVar = False
                if newYear != '' and newMonth != '' and newDay != '':
                    try:
                        newYear = int(newYear)
                    except ValueError:
                        checkVar = True
                    try:
                        newMonth = int(newMonth)
                    except ValueError:
                        checkVar = True
                    try:
                        newDay = int(newDay)
                    except ValueError:
                        checkVar = True
                    if not checkVar:
                        try:
                            dateObj = date(newYear, newMonth, newDay)
                        except ValueError:
                            pass
                        else:
                            user_info.birthday = dateObj
                            user_info.save()



                newInterests = context['addInterests']
                newInterests = newInterests.split(',')
                temporaryHold = []
                for word in newInterests:
                    temporaryHold.append(word.replace(' ',''))
                newInterests = temporaryHold

                # Creating a list of the Interest objects by their labels
                currentObjs = []
                for obj in models.Interest.objects.all():
                    currentObjs.append(str(obj))

                # If an object for a new interest does not exist, create one
                for intr in newInterests:
                    if intr not in currentObjs:
                        models.Interest(intr).save()

                # Create a list of interests that the user already has
                userObjs = []
                for ui in user_info.interests.all():
                    userObjs.append(str(ui))

                for intr in newInterests:
                    if intr not in userObjs and intr != '':
                        user_info.interests.add(models.Interest.objects.filter(label=intr))

                
        elif 'passwordChange' in request.POST:
            context = request.POST
            newPass = context['newPassword']
            user_info.user.set_password(newPass)            





        for ui in user_info.interests.all():
            interests_list.append(str(ui))
        
        
        return render(request,'account.djhtml', {'user_info': user_info, 'interests0' : interests_list})

    request.session['failed'] = True
    return redirect('login:login_view')





def people_view(request):
    """Private Page Only an Authorized User Can View, renders people page
       Displays all users who are not friends of the current user and friend requests
    Parameters
    ---------
      request: (HttpRequest) - should contain an authorized user
    Returns
    --------
      out: (HttpResponse) - if user is authenticated, will render people.djhtml
    """
    if request.user.is_authenticated:
        user_info = models.UserInfo.objects.get(user=request.user)
        interests_list = []
        for ui in user_info.interests.all():
            interests_list.append(str(ui))


        
        # TODO Objective 4: create a list of all users who aren't friends to the current user (and limit size)
        all_people = []
        friendsList = []
        peopleNotFriends = []
        for fr in user_info.friends.all():
            friendsList.append(fr)
        all_people = models.UserInfo.objects.all()
        all_people_excl_me = []
        for people in all_people:
            if people != user_info:
                all_people_excl_me.append(people)
        for people in all_people_excl_me:
            if people not in friendsList:
                peopleNotFriends.append(people)
        
        # Successfully created a list of all people excluding me and my friends
        # Create a list of friend requests
        friend_requests = []
        for fr in models.FriendRequest.objects.all():
            if fr.to_user == user_info:
                friend_requests.append(fr)

        

        # TODO Objective 5: create a list of all friend requests to current user
        

        context = { 'user_info' : user_info,
                    'peopleNotFriends' : peopleNotFriends[0:request.session['numPeople']],
                    'friend_requests' : friend_requests,
                    'interests0': interests_list }

        return render(request,'people.djhtml',context)

    request.session['failed'] = True
    return redirect('login:login_view')


def like_view(request):
    '''Handles POST Request recieved from clicking Like button in messages.djhtml,
       sent by messages.js, by updating the corrresponding entry in the Post Model
       by adding user to its likes field
    Parameters
	----------
	  request : (HttpRequest) - should contain json data with attribute postID,
                                a string of format post-n where n is an id in the
                                Post model

	Returns
	-------
   	  out : (HttpResponse) - queries the Post model for the corresponding postID, and
                             adds the current user to the likes attribute, then returns
                             an empty HttpResponse, 404 if any error occurs
    '''
    postIDReq = request.POST.get('postID')
    if postIDReq is not None:
        # remove 'post-' from postID and convert to int
        # TODO Objective 10: parse post id from postIDReq
        postID = int(postIDReq)

        if request.user.is_authenticated:
            # TODO Objective 10: update Post model entry to add user to likes field
            postFound = models.Post.objects.get(id=postID)
            user_info =  models.UserInfo.objects.get(user=request.user)
            postFound.likes.add(user_info)
            # return status='success'
            status = "success"
            return HttpResponse(status)
        else:
            return redirect('login:login_view')

    return HttpResponseNotFound('like_view called without postID in POST')

def post_submit_view(request):
    '''Handles POST Request recieved from submitting a post in messages.djhtml by adding an entry
       to the Post Model
    Parameters
	----------
	  request : (HttpRequest) - should contain json data with attribute postContent, a string of content

	Returns
	-------
   	  out : (HttpResponse) - after adding a new entry to the POST model, returns an empty HttpResponse,
                             or 404 if any error occurs
    '''
    postContent = request.POST.get('postContent')
    if postContent is not None:
        if request.user.is_authenticated:
            # TODO Objective 8: Add a new entry to the Post model
            user_info = models.UserInfo.objects.get(user=request.user)
            models.Post.objects.create(owner=user_info, content=postContent)
            # return status='success'
            status = 'success'
            return HttpResponse(status)
        else:
            return redirect('login:login_view')

    return HttpResponseNotFound('post_submit_view called without postContent in POST')

def more_post_view(request):
    '''Handles POST Request requesting to increase the amount of Post's displayed in messages.djhtml
    Parameters
	----------
	  request : (HttpRequest) - should be an empty POST

	Returns
	-------
   	  out : (HttpResponse) - should return an empty HttpResponse after updating hte num_posts sessions variable
    '''
    if request.user.is_authenticated:
        # update the # of posts dispalyed
        if (request.session['numPosts'] + 2) <= len(models.Post.objects.all()):
            request.session['numPosts'] += 2
        else:
            request.session['numPosts'] = len(models.Post.objects.all())
        # TODO Objective 9: update how many posts are displayed/returned by messages_view

        # return status='success'
        status = "success"
        return HttpResponse(status)

    return redirect('login:login_view')

def more_ppl_view(request):
    '''Handles POST Request requesting to increase the amount of People displayed in people.djhtml
    Parameters
	----------
	  request : (HttpRequest) - should be an empty POST

	Returns
	-------
   	  out : (HttpResponse) - should return an empty HttpResponse after updating the num ppl sessions variable
    '''
    if request.user.is_authenticated:
        # update the # of people dispalyed
        # TODO Objective 4: increment session variable for keeping track of num ppl displayed
        friendsList = []
        peopleNotFriends = []
        user_info = models.UserInfo.objects.get(user=request.user)
        for fr in user_info.friends.all():
            friendsList.append(fr)
        all_people = models.UserInfo.objects.all()
        all_people_excl_me = []
        for people in all_people:
            if people != user_info:
                all_people_excl_me.append(people)
        for people in all_people_excl_me:
            if people not in friendsList:
                peopleNotFriends.append(people)
        # return status='success'
        if (request.session['numPeople'] + 2) < len(peopleNotFriends):
            request.session['numPeople'] += 2
        else:
            request.session['numPeople'] = len(peopleNotFriends) 




        status = "success"
        return HttpResponse()

    return redirect('login:login_view')

def friend_request_view(request):
    '''Handles POST Request recieved from clicking Friend Request button in people.djhtml,
       sent by people.js, by adding an entry to the FriendRequest Model
    Parameters
	----------
	  request : (HttpRequest) - should contain json data with attribute frID,
                                a string of format fr-name where name is a valid username

	Returns
	-------
   	  out : (HttpResponse) - adds an etnry to the FriendRequest Model, then returns
                             an empty HttpResponse, 404 if POST data doesn't contain frID
    '''
    frID = request.POST.get('frID')
    if frID is not None:
        # remove 'fr-' from frID
        username = frID[3:]
        

        if request.user.is_authenticated:
            toUser = None
            

            for i in models.UserInfo.objects.all():
                if str(i.user) == username:
                    toUser = i
            

            fromUser = models.UserInfo.objects.get(user=request.user)            
            

            frReverseExists = False
            for i in models.FriendRequest.objects.all():
                if i.to_user == fromUser and i.from_user == toUser:
                    frReverseExists = True


            frExists = False
            for i in models.FriendRequest.objects.all(): # Checking if that friend request already exists
                if (i.to_user == toUser and i.from_user == fromUser):
                    frExists = True

            if not frExists and not frReverseExists:
                models.FriendRequest.objects.create(to_user=toUser, from_user=fromUser)

            # TODO Objective 5: add new entry to FriendRequest
            # return status='success'
            status = 'success'
            return HttpResponse(status)
        else:
            return redirect('login:login_view')

    return HttpResponseNotFound('friend_request_view called without frID in POST')

def accept_decline_view(request):
    '''Handles POST Request recieved from accepting or declining a friend request in people.djhtml,
       sent by people.js, deletes corresponding FriendRequest entry and adds to users friends relation
       if accepted
    Parameters
	----------
	  request : (HttpRequest) - should contain json data with attribute decision,
                                a string of format A-name or D-name where name is
                                a valid username (the user who sent the request)

	Returns
	-------
   	  out : (HttpResponse) - deletes entry to FriendRequest table, appends friends in UserInfo Models,
                             then returns an empty HttpResponse, 404 if POST data doesn't contain decision
    '''
    data = request.POST.get('decision')
    if data is not None:
        # TODO Objective 6: parse decision from data
        dec = data[0]
        fromUser = data[2:]
        fromUserObj = None
        for i in models.UserInfo.objects.all():
            if str(i.user) == fromUser:
                fromUserObj = i
                break
        if request.user.is_authenticated:
            user_info = models.UserInfo.objects.get(user=request.user)

            # Finding the relevant Friend Request object
            frNum = 0
            for i in range(len(models.FriendRequest.objects.all())):
                if models.FriendRequest.objects.all()[i].to_user == user_info and models.FriendRequest.objects.all()[i].from_user == fromUserObj:
                    frNum = i
            

            if dec == 'a':
                user_info.friends.add(fromUserObj)
                fromUserObj.friends.add(user_info)
                models.FriendRequest.objects.all()[frNum].delete()
            elif dec == 'd':
                models.FriendRequest.objects.all()[frNum].delete()

            



            # TODO Objective 6: delete FriendRequest entry and update friends in both Users

            # return status='success'
            return HttpResponse()
        else:
            return redirect('login:login_view')

    return HttpResponseNotFound('accept-decline-view called without decision in POST')
