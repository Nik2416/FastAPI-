from fastapi import FastAPI , Path ,HTTPException ,Query
from pydantic import BaseModel,Field,computed_field
from typing import Annotated ,Literal ,Optional
from fastapi.responses import JSONResponse
import json

app=FastAPI()

class Patient(BaseModel):
   id:Annotated[str,Field(...,description='ID of the patient',examples=['P001'])]
   name:Annotated[str,Field(...,description='Name of the patient')]
   city:Annotated[str,Field(...,description='City where patient lives')]
   age:Annotated[int,Field(...,gt=0,lt=120,description='Age of the patient')]
   gender:Annotated[Literal['male','female','others'],Field(...,description='Gender of the patient')]
   height:Annotated[float,Field(...,gt=0,description='Height of the patient in mtrs')]
   weight:Annotated[float,Field(...,gt=0,description='Weight of the patient in kgs')]

   #HERE WE WILL USE A NEW CONCEPT CALLED COMPUTED FIELD
   #WHERE WE CAN DYNAMICALLY GENERATE NEW FIELDS WITH THE HELP OF EXISTING FIELDS

   @computed_field
   @property
   def bmi(self)->float:
    bmi=round(self.weight/(self.height**2),2)
    return bmi

   @computed_field
   @property
   def verdict(self)->str:
     if self.bmi<18.5:
       return 'Underweight'
     elif self.bmi<30:
       return 'Normal'
     else:
       return 'Overweight'


class update(BaseModel):
  name:Annotated[Optional[str],Field(default=None)] 
  city:Annotated[Optional[str],Field(default=None)] 
  age:Annotated[Optional[int],Field(default=None,gt=0)] 
  gender:Annotated[Optional[Literal['male','female']],Field(default=None)] 
  height:Annotated[Optional[float],Field(default=None,gt=0)] 
  weight:Annotated[Optional[float],Field(default=None,gt=0)] 


def load_data():
  with open('ex.json','r') as f:
      data = json.load(f)

  return data

def save_data(data):
  with open('patients.json','w') as p:
     json.dump(data,p)


# Defining a route
@app.get("/")          
def hello():
  return {'message':'Patient Management System API'}

@app.get("/about") 
def about():
  return {'message':'A Fully Functional API to manage your patients records'}

@app.get("/view")
def view():
  data =load_data()
  return data


@app.get("/patient/{patient_id}")
def view_patient(patient_id:str=Path(...,description='ID of the patient in the DB ',example='P001')):
  data =load_data()

  if patient_id in data:
    return data[patient_id]
  raise HTTPException(status_code=404,detail='Patient not found')



@app.get("/sort")
def sort(sort_by:str=Query(...,description='Sort on the basis of age'),order:str=Query('asc',description='sort in asc or desc order')):

  valid_fields=['height','weight','bmi']

  if sort_by not in valid_fields:
    raise HTTPException(status_code=400,details=f'Invalid field select from {valid_fields}')

  if order not in ['asc','desc']:
    raise HTTPException(status_code=400,detail='Invalid order select between asc and desc')
  
  data=load_data()

  sort_order= True if order=='desc' else False

  sorted_data= sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sort_order)

  return sorted_data

@app.post("/create")
def create_patient(patient:Patient):   #we will recieve some data which we store in 'patient' and the type is 'Patient ' which is out PYDANTIC BASE MODEL

  #load the data 
  data =load_data()

  #check if the patient already exists
  if patient.id in  data:
    raise HTTPException(status_code=400,detail='patient already exists')
  
  #if not, then we will put our new patient in our json file

  data[patient.id]=patient.model_dump(exclude='id')

  #THIS MODEL_DUMP function change pydantic code into dictionary
  
  #SAVE THE dictionary data into json file 
  save_data(data)

  return JSONResponse(status_code=201,content={'message':'patient created successfully'})
  
@app.put('/edit/{patient_id}')
def update(pid:str,pupdate:update):
  data =load_data()

  if pid not in data:
    raise HTTPException(status_code=400,detail='patient not found')
  
  existing_pinfo=data[pid]
  updated_pinfo=pupdate.model_dump(exclude_unset=True)
  #model_dump--THis converts our pydantic model into a dictionary 
  #exclude_unset=True will only gives the value which is given by the user 
  for key,value in updated_pinfo.items():
    existing_pinfo[key]=value
  
  existing_pinfo['id']=pid 
  patient_pydantic_object=Patient(**existing_pinfo)

  existing_pinfo=patient_pydantic_object.model_dump(exclude='id')

  data[pid]=existing_pinfo
  
  save_data(data)

  return JSONResponse(status_code=200,content={'message':'patient updated'})

@app.delete('/delete/{patient_id}')
def delete_patient(pid:str):

  data=load_data()

  if pid not in data:
    raise HTTPException(status_code=404,detail='Patient not found')
  
  del data[pid]

  save_data(data)

  return JSONResponse(status_code=200,content={'message':'Patient Deleted Successfully!!'})    