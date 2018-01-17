import lxml.html as LH
import requests
import json
import re
import uuid


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def sanitize_name(sanitize_name):
    sanitize_name = re.sub("'", "", sanitize_name)
    sanitize_name = re.sub("-", "", sanitize_name)
    return sanitize_name

def create_email_for_professor(first_name,last_name):
    new_eml = first_name[0] + last_name + "@babson.edu"
    return new_eml 

def get_email_for_professor(babson_emails, professor):
    professor = professor.lower()
    professor = professor.split(",")
    print "check professor"
    print professor
    eml = None
    if len(professor) > 1:
        last_name = professor[0].lstrip().rstrip()
        first_name_word_count = len(professor[1].lstrip().rstrip().split())
        first_name = professor[1].lstrip().rstrip() if first_name_word_count == 1 else professor[1].lstrip().rstrip().split()[1] #If there is a middle name, sets first name to true first name
        middle_name = professor[1].lstrip().rstrip().split()[2] if len(first_name.split()) > 1 else "" #If there is a middle name, sets value to middle name, else it's empty
        professor_id = first_name + ";" + last_name + ";" + "none" + ";" + "employee"
        print "names"
        print first_name
        print middle_name
        print last_name
        try:
            eml_dict = babson_emails[professor_id]
            eml = eml_dict["email"]
        except KeyError: #First pass, just unsanitized first name + last name
            try:
                if first_name_word_count > 1:
                    professor_id = first_name + ";" + last_name + " " + middle_name + ";" + "none" + ";" + "employee"
                else:
                    professor_id = sanitize_name(first_name) + ";" + sanitize_name(last_name) + ";" + "none" + ";" + "employee"

                eml_dict = babson_emails[professor_id]
                eml = eml_dict["email"]
            except KeyError: #Second pass, 
                try:
                    if first_name_word_count > 1:
                        professor_id = sanitize_name(first_name) + ";" + sanitize_name(last_name) + " " + sanitize_name(middle_name) + ";" + "none" + ";" + "employee"
                        eml_dict = babson_emails[professor_id]
                        eml = eml_dict["email"]
                    else:
                        eml = create_email_for_professor(first_name,last_name)
                        print "FAILED TO FIND EMAIL. CREATING EMAIL: " + eml
                        print professor_id
                        print first_name + " " + last_name + " " + middle_name
                        print "END CREATION SINGLE"
                except KeyError:
                    try:
                        if first_name_word_count > 1:
                            professor_id = sanitize_name(first_name) + ";" + sanitize_name(last_name) + ";" + "none" + ";" + "employee"
                            eml_dict = babson_emails[professor_id]
                            eml = eml_dict["email"]
                        else:
                            print "SHOULD NEVER GO IN HERE"
                            print "BE AFRAID"
                            print eml
                    except KeyError:
                        if first_name_word_count > 1:
                            eml = create_email_for_professor(first_name,last_name)
                            print "FAILED TO FIND EMAIL FOR LONG NAME PERSON. CREATING EMAIL: " + eml
                            print professor_id
                            print first_name + " " + last_name + " " + middle_name
                            print "END CREATION LONG"
                        else:
                            print "SHOULD NEVER GO IN HERE EITHER"
                            print "BE AFRAID"
                            print eml
        
        return eml
        
        
    

    return eml

def generate_emails(babson_emails, babson_class):
    # Set empty array for professor_emails
    babson_class['professor_emails'] = []
    raw_professors_values = babson_class['professor(s)']
    if isinstance(raw_professors_values, list):
        for professor in raw_professors_values:
            email = get_email_for_professor(babson_emails, professor)
            babson_class['professor_emails'].append(email)
    else:
        email = get_email_for_professor(babson_emails, raw_professors_values)
        babson_class['professor_emails'] = [email]
    
    return babson_class['professor_emails']

        


def get_babson_classes():
    """
    This function goes into the Babson Course Listing
    Takes out all of the courses and converts them all
    as objects into one array
    """
    babson_emails = json.load(open('babson_emails.json'))

    all_babson_classes = []  # Will contain all of the class objects
    #  Call initial Babson Course Log
    url = 'https://fusionmx.babson.edu/CourseListing/index.cfm?fuseaction=CourseListing.DisplayCourseListing&blnShowHeader=false&program=Undergraduate&semester=All&sort_by=course_number&btnSubmit=Display+Courses'
    page = requests.get(url)
    # Turn page html string into lxml HTML object
    html = LH.fromstring(page.text)
    data = html.xpath("*")
    # Get the body element object
    body_element = data[1]
    tables = body_element.xpath('table')
    tr_elements = []

    # Iterates over the 4 major semester tables to assign the semester to each for loop of trs
    for table in tables:
        tr_elements = []
        tr = table.xpath('tr')
        semester = table.xpath('tr/td/*/tr')[0].xpath('*/text()')
        all_trs = tr[0].xpath('td')[0].xpath('table')[0].xpath('tr')
        for tr in all_trs:
            for div in tr.xpath('td')[0].xpath('div'):
                for tr in div.xpath('*')[0].xpath('*'):
                    tr_elements.append(tr)

        # 1 tr_element = 1 class listing
        for tr in tr_elements:
            class_object = {}
            td_array = []
            for td in tr.xpath('td'):
                count = 0
                class_a_tags = td.xpath("a")
                if len(class_a_tags) == 1:
                    course_name = class_a_tags[0].xpath("text()")[0]
                    td_array.append(course_name)
                else:
                    try:
                        course_data = td.xpath("text()")
                        course_data_point_array = []
                        if len(course_data) > 1:
                            for course_data_point in course_data:
                                course_data_point = re.sub(
                                    '\s+', '', course_data_point)
                                course_data_point = course_data_point.replace(
                                    ",", " ")
                                if "WebEx" in course_data_point:
                                    pass
                                else:
                                    course_data_point_array.append(
                                        str(course_data_point))
                            td_array.append(course_data_point_array)
                        else:
                            td_array.append(course_data[0])
                    except:
                        pass
            # try:
            class_object['class_name'] = td_array[2].title()
            class_object['course_code'] = td_array[1]

            # If course code is in position 4 of the array
            # The following if else function reassigns value positions based on if the
            # course has a time of the day
            if '-' in td_array[3]:
                class_object['day_of_week'] = "".join(
                    " ".join(td_array[3].split(' ')[0:2]).split())
                class_object['time'] = "".join(
                    " ".join(td_array[3].split(' ')[2:]).split())
                prof_place = 4
                class_room_place = 5
                spots_filled_place = 6
                credits_place = 7
                session_place = 8
            else:
                prof_place = 3
                class_room_place = 4
                spots_filled_place = 5
                credits_place = 6
                session_place = 7

            class_object['class_room'] = td_array[class_room_place]
            class_object['session'] = td_array[session_place]
            class_object['semester'] = "".join(semester[0].split())
            class_object['credits'] = td_array[credits_place]
            class_object['spots_filled_string'] = td_array[spots_filled_place]
            class_object['professor(s)'] = td_array[prof_place]
            if isinstance(class_object['professor(s)'], list):
                for idx, val in enumerate(class_object['professor(s)']):
                    class_object['professor(s)'][idx] = val.lstrip(
                    ).rstrip()
            else:
                class_object['professor(s)'] = td_array[prof_place].lstrip(
                ).rstrip()
            spots_filled = td_array[spots_filled_place]

            spots_taken = "".join("of".join(spots_filled.split('of')[0:1]).split())
            spots_available = "".join("of".join(spots_filled.split('of')[1:]).split())
            
            if is_number(spots_taken):
                class_object['spots_taken'] = int(spots_taken)
            else:
                class_object['spots_taken'] = spots_taken
            
            if is_number(spots_available):
                class_object['spots_available'] = int(spots_available)
            else:
                class_object['spots_available'] = spots_available
            class_object['course_code'] = "".join(
                "-".join(td_array[1] .split('-')[0:1]).split())
            class_object['course_section'] = "".join(
                "-".join(td_array[1] .split('-')[1:]).split())

            # print class_object
            # print td_array[1]
            # print "-"
            # print "".join(" ".join(td_array[3].split(' ')[2:]).split())
            # print "-"
            # print "".join(" ".join(td_array[prof_place].split(
            #     ' ')[2:]).split())
            # print "-"
            # print "".join(" ".join(td_array[spots_filled_place].split(' ')[2:]).split())
            # print "".join(semester[0].split())
            # print td_array[class_room_place]

            #This is doing way too much...
            # class_object['unique_key_internal'] = td_array[1] + "-" + "".join(" ".join(td_array[3].split(' ')[2:]).split()) + "-" + "".join(" ".join(td_array[prof_place].split(
            #     ' ')[2:]).split()) + "-" + "".join(" ".join(td_array[spots_filled_place].split(' ')[2:]).split()) + "".join(semester[0].split()) + td_array[class_room_place]  


            # This is just to have a unique key per class listing. The course code codes are sometimes repeated.
            class_object["unique_key_internal"] = str(uuid.uuid4())
            
            all_babson_classes.append(class_object)

    # Add in Babson Professor emails to the json output
    for babson_class in all_babson_classes:
        babson_class['professor_emails'] = generate_emails(babson_emails, babson_class)
        # Give all classes empty profesor email array
        # professor_emails = []
        # babson_class['professor_emails'] = professor_emails
        # print "CHECK BELOW"
        # print babson_class['professor(s)']
        # # If there is more than one professor, just run function
        # if isinstance(babson_class['professor(s)'], list):

        #     for professor in babson_class['professor(s)']:
        #         professor = professor.lower()
        #         professor = professor.split()
        #         print "this professor"
        #         print professor
        #         print len(professor)
        #         if len(professor) > 2:
        #             print "yo dawg look double"

        #         if len(professor) > 1:
        #             print professor
        #             professor_id = professor[1] + ";" + \
        #                 professor[0] + ';none;employee'
        #             professor_id = re.sub(',', '', professor_id)
        #             print professor_id
        #             # print professor_id
        #             try:
        #                 babson_class['auto_generated_email'] = False
        #                 eml = babson_emails[str(professor_id)]['email']
        #                 print eml
        #                 babson_class['professor_emails'].append(eml)
        #             except:
        #                 print "EXCEPT!"
        #                 babson_class['auto_generated_email'] = True
        #                 print professor[0]
        #                 professor[0] = professor[0].translate(None, ' ')
        #                 professor[0] = professor[0].translate(None, ',')
        #                 professor[0] = professor[0].translate(None, '\t\n')
        #                 professor[0] = professor[0].replace(" ", "")
        #                 print professor[0]
        #                 new_email = professor[1][:1] + \
        #                     professor[0] + '@babson.edu'
        #                 print new_email
        #                 new_email = new_email.translate(None, ' ')
        #                 new_email = new_email.translate(None, ',')
        #                 new_email = new_email.translate(None, '\t\n')
        #                 new_email = new_email.split(" ")
        #                 print new_email
        #                 babson_class['professor_emails'].append(new_email[0])
        #         # else:
        #         #     print "ARJUN HERE"
        #         #     print professor
        #         #     print class_object['time']
        #         #     print class_object['day_of_week']

        # # If there is only one professork, create array for them and then run function
        # else:
        #     print "SINGLE PROFESSOR"
        #     professor_array = []
        #     professor_array.append(babson_class['professor(s)'])
        #     babson_class['professor(s)'] = professor_array
        #     professor = professor_array[0].lower()
        #     professor = professor.split()
        #     print "single guy"
        #     print professor
        #     print len(professor)
        #     if len(professor) > 2:
        #         print "yo dawg look single"

        #     if len(professor) > 1:
        #         professor_id = professor[1] + ";" + \
        #             professor[0] + ';none;employee'
        #         professor_id = re.sub(',', '', professor_id)
        #         # print professor_id
        #         try:
        #             babson_class['auto_generated_email'] = False
        #             eml = babson_emails[str(professor_id)]['email']
        #             print eml
        #             babson_class['professor_emails'].append(eml)
        #         except:
        #             print "SINGLE EXCEPT"
        #             babson_class['auto_generated_email'] = True
        #             print professor[0]
        #             professor[0] = professor[0].translate(None, ' ')
        #             professor[0] = professor[0].translate(None, ',')
        #             professor[0] = professor[0].translate(None, '\t\n')
        #             professor[0] = professor[0].replace(" ", "")
        #             print professor[0]
        #             new_email = professor[1][:1] + professor[0] + '@babson.edu'
        #             print new_email
        #             new_email = new_email.translate(None, ' ')
        #             new_email = new_email.translate(None, ',')
        #             new_email = new_email.translate(None, '\t\n')
        #             new_email = new_email.split(" ")
        #             print new_email
        #             babson_class['professor_emails'].append(new_email[0])

    return all_babson_classes


def check_babson_class_emails(classes):
    print '---------------------------'
    email_count = 0
    for babson_class in classes:
        if len(babson_class['professor_emails']) > 0:
            for email in babson_class['professor_emails']:
                # print email
                pass
            email_count += 1
        else:
            # print  babson_class['professor(s)']
            pass
    print '---------------------------'
    print 'Number of Classes: ' + str(len(classes))
    print 'Number of Found Emails: ' + str(email_count)
    print '---------------------------'


check_babson_class_emails(get_babson_classes())
