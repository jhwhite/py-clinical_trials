import os, zipfile, urllib.request
from elasticsearch import Elasticsearch
import xml.etree.ElementTree as ET

# Function to put the keywords into a list. I want to call this an array. Will anyone really mind?
def create_keyword_list(keywords):
    return keywords.split(',')

# Function to strip '\n' from data.
def strip_newlines(strings):
    return strings.replace("\n", "<br />")

# Function to strip 6 extra spaces.
def strip_extra_spaces(strings):
    return " ".join(strings.split())

# Let's connect to Elasticsearch!
es = Elasticsearch()

# Delete the index each time because some trials will be removed and I don't want to display trials that may not be available anymore. But, if the status changes, then the document will be udpated accordingly. Correct? Or is this still just safer?
#es.indices.delete(index="clinical_trials")

# Downloading the zip file using urllib.
remote_file = urllib.request.urlretrieve('http://clinicaltrials.gov/ct2/results?term=&recr=Recruiting&rslt=&type=&cond=&intr=&titles=&outc=&spons=&lead=&id=&state1=&cntry1=&state2=&cntry2=&state3=&cntry3=&locn="university+of+virginia"&gndr=&rcv_s=&rcv_e=&lup_s=&lup_e&studyxml=true', "/Users/jhwhite/python-projects/py-clinical_trials/search_result.zip")


# Set the path to where the unzipped trials will be placed. 
path = '/Users/jhwhite/python-projects/py-clinical_trials/search_results/'

# Check to see if the path actually exists. If it doesn't, create it.
if not os.path.exists(path):
    os.makedirs(path)

# Unzips the download and then puts the contents in the path from above
z = zipfile.ZipFile('/Users/jhwhite/python-projects/py-clinical_trials/search_result.zip')
z.extractall(path)

# Now how about getting a list of the files that we just unzipped?
dirs = os.listdir( path )

# Loop through each xml file and pull out the information we're after
for file in dirs:

    #print( file)
   
    tree = ET.parse(path + file)
    root = tree.getroot()
    # #print( root)

    bt = root.find("brief_title").text
    #print( "brief title: " + bt)
   
    official_title = root.find("official_title")
    if official_title is not None:
        ot = root.find("official_title").text
        #ot = strip_newlines(ot)
    else:
        ot = "No official title provided"
    #print( "official title: " + ot)

    brief_summary = root.find("brief_summary")
    if brief_summary is not None:
        bs = root.find("brief_summary")[0].text
        #bs = strip_newlines(bs)
        #bs = strip_extra_spaces(bs)
    else:
        bs = "No brief summary provided"
    #print( "brieft summary: " + bs)

    detailed_description = root.find("detailed_description")
    if detailed_description is not None:
        dd = root.find("detailed_description")[0].text

        #dd = strip_newlines(dd)
        #dd = strip_extra_spaces(dd)
    else:
        dd = "No detailed description provided"
    #print( "detailed_description: " + dd)

    eligibility = root.find("eligibility/criteria/textblock")
    if eligibility is not None:
        e = root.find("eligibility/criteria/textblock").text
        #e = strip_newlines(e)
        #e = strip_extra_spaces(e)
    else:
        e = "No eligibility provided"
    #print( "eligibility: " + e)

    gender = root.find("eligibility/gender")
    if gender is not None:
        g = root.find("eligibility/gender").text
        #g = strip_newlines(g)
    else:
        g = "No gender provided"
    #print( "gender: " + g)

    min_age = root.find("eligibility/minimum_age")
    if min_age is not None:
        minimum = root.find("eligibility/minimum_age").text
        #minimum = strip_newlines(minimum)
    else:
        minimum = "No minimum age provided"
    #print( "minimum age: " + minimum)

    max_age = root.find("eligibility/maximum_age")
    if max_age is not None:
        maximum = root.find("eligibility/maximum_age").text
        #maximum = strip_newlines(maximum)
    else:
        maximum = "No maximum age provided"
    #print( "maximum age: " + maximum)

    healthy = root.find("eligibility/healthy_volunteers")
    if healthy is not None:
        hv = root.find("eligibility/healthy_volunteers").text
        if hv != "No":
            hv = "Yes"
        #hv = strip_newlines(hv)
        print(hv)
    else:
        hv = "No information about healthy volunteers provided"
    #print( "healthy volunteers: " + hv)

    link = root[0][2].text
    #print( link)

    date = root[0][0].text
   
    keyword_list = []
    if root.find('keyword') is not None:
        keywords = [events.text for events in root.findall('keyword')]
        kw = ','.join(keywords)
        kw = create_keyword_list(kw)
    else:
        kw = []
    #print("Keywords: {}".format(kw))

    overall_status = root.find("overall_status")
    if root.find('overall_status') is not None:
        os = root.find('overall_status').text
        #os = strip_newlines(os)
    else:
        os = "No overall status provided"

    for location in root.getiterator('location'):
        if location.find('facility/name') is not None:
            loc = location.find('facility/name').text
            if "University of Virginia" in loc:
                location_name = loc
                if location.find('facility/address/city') is not None:
                    city = location.find('facility/address/city').text
                else:
                    city = "Not provided"
                #print(city)
                if location.find('facility/address/zip') is not None:
                    loc_zip = location.find('facility/address/zip').text
                else:
                    loc_zip = "Not provided"
                #print( loc_zip)
                if location.find('status') is not None:
                    status = location.find('status').text
                else:
                    status = "Not status provided"
                #print( status)
                if location.find('contact/last_name') is not None:
                    last_name = location.find('contact/last_name').text
                else:
                    last_name = "Not provided"
                #print( last_name)
                if location.find('contact/phone') is not None:
                    phone = location.find('contact/phone').text
                else:
                    phone = "Not provided"
                #print( phone)
                if location.find('contact/email') is not None:
                    email = location.find('contact/email').text
                else:
                    email = "Not provided"
                #print( email)
                if location.find('investigator/last_name') is not None:
                    principal_investigator = location.find('investigator/last_name').text
                else:
                    principal_investigator = "Not provided"

    # For each file we'll send the information to Elasticsearch
    es.index(index='clinical_trials', doc_type='trial', id=file, body={
        'brief_title': bt,
        'official_title': ot,
        'brief_summary': bs,
        'detailed_description': dd,
        'eligibility': e,
        'gender': g,
        'minimum_age': minimum,
        'maximum_age': maximum,
        'healthy_volunteers': hv,
        'link': link,
        'keywords': kw,
        'overall_status': os,
        'city': city,
        'zip': loc_zip,
        'status': status,
        'name': last_name,
        'phone_number': phone,
        'email_address': email,
        'facility': location_name,
        'date': date,
        'principal_investigator': principal_investigator
        })
