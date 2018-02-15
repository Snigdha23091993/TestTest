from flask import Flask,render_template,jsonify,request, redirect, session
import requests
import json
from dropbox import DropboxOAuth2Flow
from DisplayFiles import *
from dropbox.oauth import BadRequestException, BadStateException, CsrfException, NotApprovedException, ProviderException
from dropbox import sharing
from dropbox import dropbox
from dropbox import files
import os,io
app=Flask(__name__)

@app.route("/")
def index():
	return render_template("home.html")

# Return webpage...redirect to webpage............
@app.route("/show/<myname>")
def showMyName(myname):
	#return "Index Page...."+myname
	return render_template("home.html")

# Retrun Data....JSON dictionary
@app.route("/json_data")
def Jsondata():
	my_info={"Snigdha":120,
		"ABC":25}
	return jsonify(my_info)

@app.route("/start_flow",methods=['GET'])
def dropbox_auth_redirect():
    print("Inside Start Flow....")
    redirect_uri="http://127.0.0.1:5000/dropbox_auth"
    url = get_auth_url(session, redirect_uri)
    print("Redirect URL : %s" % url)
    return redirect(url)

def get_auth_url(session, redirect_uri):
    print("Get Auth Url.........")
    return get_dropbox_auth_flow(session).start()

def get_dropbox_auth_flow(session):
    print("Inside get_dropbox_auth_flow() function....")
    redirect_uri = "http://127.0.0.1:5000/dropbox_auth"
    APP_KEY="ikm5mj303w3iuoa"
    APP_SECRET="fmql9qv0l5vaapw"
    web_app_session=session
    return DropboxOAuth2Flow(APP_KEY, APP_SECRET, redirect_uri, web_app_session,"dropbox-auth-csrf-token")


#URL handler for /dropbox-auth-start
def dropbox_auth_start(session, request):
    authorize_url = get_dropbox_auth_flow(session).start()
    redirect_to(authorize_url)

#URL handler for /dropbox-auth-finish
def dropbox_auth_finish(session, request):
    try:
    	  oauth_result =get_dropbox_auth_flow(session).finish(request)
    	  print(oauth_result.access_token)
    	  session['access_token']=oauth_result.access_token
    	  
    except BadRequestException as e:
        http_status(400)
    except BadStateException as e:
        # Start the auth flow again.
        redirect_to("/dropbox-auth-start")
    except CsrfException as e:
        http_status(403)
    except NotApprovedException as e:
        flash('Not approved?  Why not?')
        return redirect_to("/home")
    except ProviderException as e:
        logger.log("Auth error: %s" % (e,))
        http_status(403)	

@app.route('/dropbox_auth', methods=['GET'])
def redirectedToAuth():
	print("Ok......")
	state = request.args.get('state')
	print("state : %s  "%state)
	code = request.args.get('code')
	print("code  : %s  "%code)
	
	dropbox_auth_finish(session, { 'state': state, 'code': code })
	
	return render_template("home.html")

@app.route("/received_files")
def ReceivedFiles():
	
	dbx=Dropbox(session['access_token']);
	print("Inside Received Files")
	myfiles=dbx.sharing_list_received_files(limit=100, actions=None)
	print("\n*-*----*--*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-* MY FILES -*-*-*-*-*--*---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\n")
	print(myfiles)
	for f in myfiles.entries:
		print(f.name+" ------"+f.id)

	'''folders=dbx.sharing_list_mountable_folders(limit=1000, actions=None)
	for fd in folders.entries:
		print(fd.access_type)
		print(fd.is_inside_team_folder)
		print(fd.name)
		member_info=dbx.sharing_list_folder_members(fd.shared_folder_id, actions=None, limit=1000)	
		print("\n =*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*"+fd.name+"=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*\n")
		#print(member_info)
	#file_metadata=dbx.sharing_mount_folder("1964371760")
	#print(file_metadata)
	shared_links=dbx.sharing_list_shared_links(path=None, cursor=None, direct_only=None) # return shared links
	account_id=["dbid:AAA7Z0QTIR3cT6r1El4tgddBTpf3Ib7Mbwg","dbid:AADVB4bV3q6XNX6SiDUWDDFDJHjX7wMnZ_w"]
	acc_info=getUser_info(account_id)
	print("\n\n")
	print(acc_info)'''
	'''file_data=dbx.files_get_metadata("/image101.png", include_media_info=False, include_deleted=False, include_has_explicit_shared_members=False)
	print(file_data)'''
	
	'''folders=dbx.sharing_list_folders(limit=1000, actions=None)
	print("*-*----*--*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-----*---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
	print(folders)
	print("*-*----*--*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-----*---*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")'''
	return render_template("home.html")
	#return render_template("home.html",data=myfiles.entries,folders=folders.entries,links=shared_links.links)	


def getUser_info(account_id):
	
	url="https://api.dropboxapi.com/2/users/get_account_batch"
	data = {
		"account_ids": account_id
	}
	data_json = json.dumps(data)
	
	headers = {
	    "Authorization": "Bearer "+session['access_token'],
	    "Content-Type": "application/json"
	}
	response = requests.post(url, data=data_json, headers=headers)
	return response.text

@app.route("/files_download")
def DownloadFiles():
	dbx=Dropbox(session['access_token']);
	dbx.files_download_to_file("/fromDropBox.py","/test101.py",rev=None)
	return render_template("home.html")
	
@app.route("/share_file")
def ShareFiles():

	url="https://api.dropboxapi.com/2/sharing/add_file_member"
	data = {
    		"file": "id:JKe4IRlowJAAAAAAAAAACQ",
    		"members": [
       			 {
            		".tag": "email",
            		"email": "snigdha.kadam@anveshak.com"
        		}
    			],
    		"custom_message": "id:JKe4IRlowJAAAAAAAAAAHg file id...",
   		"quiet": False,
    		"access_level": "viewer",
    		"add_message_as_comment": False
		}
	data_json = json.dumps(data)
	headers = {
	    "Authorization": "Bearer "+session['access_token'],
	    "Content-Type": "application/json"
	}
	response = requests.post(url, data=data_json, headers=headers)
	print("@ File Shared@")
	print(response)
	return render_template("home.html")
@app.route("/automount-files")
def AutoMountFiles():
	dbx=Dropbox(session['access_token']);
	#download_path="DirImg/ganapati.png"
	#src_path = os.path.join('/', download_path)
	#print(download_path)
	#statinfo = os.stat(download_path)
	#FILE_SIZE=statinfo.st_size
	#print(FILE_SIZE)
	CHUNK_SIZE = 4 * 1024 * 1024
	'''print(CHUNK_SIZE)
	file_obj=open(download_path,"rb")
	dbx.files_upload(file_obj.read(CHUNK_SIZE), "/Test/ganapati.png")
	if FILE_SIZE > CHUNK_SIZE:
		print("Use session_upload method  files_upload_session_start()")
	else:
		print("Use file_upload method ..... files_upload()  ")'''
	dir_path="TestingDirectory"
	if not os.path.exists(dir_path):
		print("Make New Directory")	
		os.mkdir(dir_path)
	rmpath=os.path.join('',dir_path+"/bts.jpg")
	#os.remove(rmpath)
	os.rmdir(dir_path)
	myfiles=dbx.sharing_list_received_files(limit=100, actions=None)
	print("-==-=-===-=-==-==-=-=-=-==-=-===  received files -==-=-=-=-==-=-===-=-==-==-=-=-=-==-=-===-=-==-==-=-=-=")
	print(myfiles.entries)
	all_files=dbx.files_list_folder("")
	print("\n\n*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*- My Files *-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
	print(all_files.entries)
	'''for f in myfiles.entries:
		print(f.id)
		print(f.preview_url)
		url=f.preview_url
		
		download_path=dir_path+"/"+f.name
		print(download_path)
		print("********************************************************************")
		file_info=dbx.sharing_get_shared_link_file_to_file(download_path, url, path=None, link_password=None)
		print("Downloaded....")
		
		statinfo = os.stat(download_path)
		FILE_SIZE=statinfo.st_size
		src_path = os.path.join('', download_path)
		file_obj=open(src_path,"rb")
		DEST_PATH="/"+f.name;
		print(FILE_SIZE)
		if FILE_SIZE > CHUNK_SIZE:
			print("Use seyssion_upload method  files_upload_session_start()")
		else:
			print("Use file_upload method ..... files_upload()  ")
			dbx.files_upload(file_obj.read(CHUNK_SIZE), DEST_PATH)

		print("-	-	-	-	-	-	-	-	-	-	\n\n")
		'''
	return render_template("home.html")

@app.route("/download-file")
def DownloadFile():
	'''url = "https://content.dropboxapi.com/2/sharing/get_shared_link_file"

	headers = {
    "Authorization": "Bearer hyVW8CO6vtAAAAAAAAAB90w-0QhJ_Q5D6pJujMmOZ7W8swW5vXOtm_MVDnS0esbN",
    "Dropbox-API-Arg": "{\"url\":\"https://www.dropbox.com/scl/fi/xyn2p1zvnok9g9lit8a81/ERP%20changes.txt?dl=0\"}"
}

	r = requests.post(url, headers=headers)
	print(r.text)
	fh = open("Changes.txt","w")
	fh.write(r.text)'''
	dbx=Dropbox(session['access_token']);
	url='https://www.dropbox.com/scl/fi/s80kaz8jczya5e2aioo5y/ganapati.png?dl=0'
	download_path="ganapati.png"
	file_info=dbx.sharing_get_shared_link_file_to_file(download_path, url, path=None, link_password=None)

	return render_template("home.html")

@app.route("/share_folder")
def ShareFolders():
	shared_id=MakeFolderSharable("/DIGITILE MASTER SHARING")
	'''url="https://api.dropboxapi.com/2/sharing/add_file_member"
	data = {
    		"shared_folder_id": "1957222400",
    		"members": [
       			 {
            		".tag": "email",
            		"email": "snigdha.kadam@anveshak.com"
        		}
    			],
    		"custom_message": "id:1957222400 Demo Folder file id...",
   		"quiet": False,
    		"access_level": "viewer",
    		"add_message_as_comment": False
		}
	data_json = json.dumps(data)
	headers = {
	    "Authorization": "Bearer "+session['access_token'],
	    "Content-Type": "application/json"
	}'''
	#response = requests.post(url, data=data_json, headers=headers)
	#print(" $ Folder Shared $ ")
	#print(response)
	return render_template("home.html")



def MakeFolderSharable(folder_path):
	print("Make folder sharable.........")
	url="https://api.dropboxapi.com/2/sharing/share_folder"
	data={
		    "path": folder_path, #The path to the folder to share. If it does not exist, then a new one 								is created. 
		    "acl_update_policy": "editors", #Who can add and remove members of this shared folder. This field is 									optional.
		    "force_async": False, # Boolean Whether to force the share to happen asynchronously.default False
		    "member_policy": "team",	# team-- Void Only a teammate can become a member.
					    	# anyone-- Void Anyone can become a member. 
		    
		}
	data_json = json.dumps(data)
	headers = {
	    "Authorization": "Bearer "+session['access_token'],
	    "Content-Type": "application/json"
		}
	response = requests.post(url, data=data_json, headers=headers)
	print("999999999999999999999999999999999999999   Shared Folder Id   999999999999999999999999999999999999999999")
	#print(response.text)
	json_res=json.loads(response.text)
	print(json_res.shared_folder_id)
	return response.text

@app.route("/create_folder")
def create_folder():
	url="https://api.dropboxapi.com/2/files/create_folder_v2"
	headers = {
	    "Authorization": "Bearer "+session['access_token'],
	    "Content-Type": "application/json"
	}
	data={
	    "path": "/Digitile Shared Files/Digitile Shared Files_ViewOnly_Files",
	    "autorename": True
	}
	data_json = json.dumps(data)
	response = requests.post(url, data=data_json, headers=headers)
	message="Folder created !! "
	print(response.text)
	return render_template("home.html",message=message)


@app.route("/my_files")
def displayFiles():
	print("Inside Ok....")
	dbx=Dropbox(session['access_token']);

	all_files=dbx.files_list_folder("")
	for ff in all_files.entries:
		print("((((((((((((((((((((((((((((((((9")
		file_data=dbx.files_get_metadata(ff.path_lower, include_media_info=True, include_deleted=True, include_has_explicit_shared_members=True)
		print(file_data)
	
	#for file in all_files.entries:
		#print(file)
	'''url = "https://api.dropboxapi.com/2/sharing/list_received_files"

	headers = {
	    "Authorization": "Bearer "+session['access_token'],
	    "Content-Type": "application/json"
	}
	data = {
		"limit":100,
		"actions":[]	
	}
	r = requests.post(url, headers=headers, data=json.dumps(data))	
	dt=r.json()
	print("\n\n")
	print(r.content)
	for a in range(len(dt['entries'])):
		print(dt['entries'][a])
	print("Hi........")'''
	return render_template("home.html",data=all_files.entries)	

if __name__ =="__main__":
	app.secret_key = 'super secret key'
	app.config['SESSION_TYPE'] = 'filesystem'
	app.run(debug=True)








'''  dt='{"entries": [{"access_type": {".tag": "viewer"}, "id": "id:dw7yJpBZHLAAAAAAAAAABQ", "name": "Get Started with Dropbox.pdf", "permissions": [], "policy": {"acl_update_policy": {".tag": "editors"}, "shared_link_policy": {".tag": "anyone"}, "viewer_info_policy": {".tag": "enabled"}}, "preview_url": "https://www.dropbox.com/scl/fi/ye0e16bfyjz03m9kuu0hx/Get%20Started%20with%20Dropbox.pdf?dl=0", "time_invited": "2017-12-06T11:21:42Z"}, {"access_type": {".tag": "viewer"}, "id": "id:dw7yJpBZHLAAAAAAAAAADA", "name": "restaurant-desktop-background.jpeg", "permissions": [], "policy": {"acl_update_policy": {".tag": "editors"}, "shared_link_policy": {".tag": "anyone"}, "viewer_info_policy": {".tag": "enabled"}}, "preview_url": "https://www.dropbox.com/scl/fi/y3vllq8ptp2fjjgxyaxc2/restaurant-desktop-background.jpeg?dl=0", "time_invited": "2017-12-06T12:05:36Z"}]} '''
