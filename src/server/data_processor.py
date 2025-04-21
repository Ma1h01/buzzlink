import json
from typing import List, Optional
from langchain.docstore.document import Document

def _get_with_condition(dictionary: dict, key: str, condition_values: List = [None, ""], default: str = "Unknown") -> str:
    """Helper function to get values from dictionary with condition checking."""
    value = dictionary.get(key, default)
    return default if value in condition_values else value

def preprocess_alumni_profile(data_path: str) -> List[Document]:
    """
    Create one document for each alumnus JSON profile, and return a list of documents.
    These documents are then stored in a vector store for later retrieval.
    These documents contain a summary of the alumnus's work experiences and education history with their names, LinkedIn URLs and profile pictures as metadata.
    """
    with open(data_path, 'r') as f:
        alumni_profiles = json.load(f)
        documents = []
        for alumnus in alumni_profiles:
            companies = set()
            id, name = _get_with_condition(alumnus, 'id'), _get_with_condition(alumnus, "name")
            about = _get_with_condition(alumnus, "about")
            headline = _get_with_condition(alumnus, "headline")
            location = _get_with_condition(alumnus, "location")
            profile_pic = _get_with_condition(alumnus, "profile_pic")
            experiences = _get_with_condition(alumnus, "experiences")
            educations = _get_with_condition(alumnus, "educations")
            
            intro_line = f"{name} is a {headline} at {location}. {name} self-describes as {about}."
            exp_lines = [f"{name}'s work experiences are as follows:"]
            edu_lines = [f"{name}'s education history is as follows:"]
            
            for idx, exp in enumerate(experiences):
                title = _get_with_condition(exp, "title")
                company = _get_with_condition(exp, "company")
                work_type = _get_with_condition(exp, "work_type")
                location = _get_with_condition(exp, "location")
                start = _get_with_condition(exp, "start_date")
                end = _get_with_condition(exp, "end_date")
                description = _get_with_condition(exp, "description")
                
                exp_lines.append(
                    f"{idx+1}. Role: {title}\n"
                    f"Company: {company}\n"
                    f"Work Type: {work_type}\n"
                    f"Location: {location}\n"
                    f"Duration: {start} to {end}\n"
                    f"Description: {description}"
                )
                companies.add(company)
                
            for idx, edu in enumerate(educations):
                school = _get_with_condition(edu, "school")
                degree = _get_with_condition(edu, "degree")
                major = _get_with_condition(edu, "major")
                start = _get_with_condition(edu, "start_date")
                end = _get_with_condition(edu, "end_date")
                description = _get_with_condition(edu, "description")
                
                edu_lines.append(
                    f"{idx+1}. School: {school}\n"
                    f"Degree: {degree}\n"
                    f"Major: {major}\n"
                    f"Duration: {start} to {end}\n"
                    f"Description: {description}"
                )

            alumnus_profile_summary = f"{intro_line}\n\n" + "\n".join(exp_lines) + "\n\n" + "\n".join(edu_lines)
            doc = Document(
                page_content=alumnus_profile_summary,
                metadata={
                    "id": id,
                    "name": name,
                    "profile_pic": profile_pic,
                    "companies": list(companies)
                }
            )
            documents.append(doc)
        return documents

def preprocess_alumni_profile_with_manual_split(data_path: str) -> List[Document]:
    """
    Create one or more documents for each alumnus JSON profile based on the split, and return a list of documents.
    These documents are then stored in a vector store for later retrieval.
    
    Each profile will have the following splits:
    - summary: {page_content: <headline+location+bio>, metadata:{id, pic, name, location, role, company, work_type, work_duration, school, degree, major, school_duration}}
    - each work exp: {page_content: <title+company+work_type+start_date+end_date+location+description>, metadata:{...}}
    - each edu hist: {page_content: <school+degree+major+start_date+end_date+description>, metadata:{...}}
    """
    with open(data_path, 'r') as f:
        alumni_profiles = json.load(f)
        documents = []
        for alumnus in alumni_profiles:
            # Extract basic info
            id = _get_with_condition(alumnus, 'id')
            name = _get_with_condition(alumnus, "name")
            about = _get_with_condition(alumnus, "about")
            headline = _get_with_condition(alumnus, "headline")
            location = _get_with_condition(alumnus, "location")
            profile_pic = _get_with_condition(alumnus, "profile_pic")
            experiences = _get_with_condition(alumnus, "experiences")
            educations = _get_with_condition(alumnus, "educations")

            # Create summary document
            summary_line = f"{name} is a {headline} at {location}. {name} self-describes as {about}"
            summary_doc = Document(
                page_content=summary_line,
                metadata={
                    "id": id,
                    "name": name,
                    "profile_pic": profile_pic,
                    "location": location,
                    "role": None,
                    "company": None,
                    "work_type": None,
                    "work_duration": None,
                    "school": None,
                    "degree": None,
                    "major": None,
                    "school_duration": None
                }
            )
            documents.append(summary_doc)

            # Create work experience documents
            for exp in experiences:
                title = _get_with_condition(exp, "title")
                company = _get_with_condition(exp, "company")
                work_type = _get_with_condition(exp, "work_type")
                work_location = _get_with_condition(exp, "location")
                start = _get_with_condition(exp, "start_date")
                end = _get_with_condition(exp, "end_date")
                description = _get_with_condition(exp, "description")
                
                exp_line = (
                    f"Name: {name}\n"
                    f"Role: {title}\n"
                    f"Company: {company}\n"
                    f"Work Type: {work_type}\n"
                    f"Location: {work_location}\n"
                    f"Duration: {start} to {end}\n"
                    f"Description: {description}"
                )
                
                work_doc = Document(
                    page_content=exp_line,
                    metadata={
                        "id": id,
                        "name": name,
                        "profile_pic": profile_pic,
                        "location": work_location,
                        "role": title,
                        "company": company,
                        "work_type": work_type,
                        "work_duration": f"{start} to {end}",
                        "school": None,
                        "degree": None,
                        "major": None,
                        "school_duration": None
                    }
                )
                documents.append(work_doc)

            # Create education documents
            for edu in educations:
                school = _get_with_condition(edu, "school")
                degree = _get_with_condition(edu, "degree")
                major = _get_with_condition(edu, "major")
                start = _get_with_condition(edu, "start_date")
                end = _get_with_condition(edu, "end_date")
                description = _get_with_condition(edu, "description")
                
                edu_line = (
                    f"School: {school}\n"
                    f"Degree: {degree}\n"
                    f"Major: {major}\n"
                    f"Duration: {start} to {end}\n"
                    f"Description: {description}"
                )
                
                edu_doc = Document(
                    page_content=edu_line,
                    metadata={
                        "id": id,
                        "name": name,
                        "profile_pic": profile_pic,
                        "location": None,
                        "role": None,
                        "company": None,
                        "work_type": None,
                        "work_duration": None,
                        "school": school,
                        "degree": degree,
                        "major": major,
                        "school_duration": f"{start} to {end}"
                    }
                )
                documents.append(edu_doc)

        return documents 