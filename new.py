from fastapi import FastAPI
from pydantic import BaseModel,Field,computed_field
from fastapi.responses import JSONResponse
from typing import Literal , Annotated
import pickle
import pandas as  pd

with open("model.pkl","rb") as f:
   model=pickle.load(f)


app=FastAPI()

tier_1= [
    "Ahmedabad", "Bengaluru", "Chennai", "Delhi",
    "Hyderabad", "Kolkata", "Mumbai", "Pune"
]
tier_2 = [
    "Agra", "Ajmer", "Amritsar", "Chhatrapati Sambhajinagar",
    "Bhopal", "Bhubaneswar", "Chandigarh", "Coimbatore", "Cuttack",
    "Dehradun", "Dhanbad", "Durg-Bhilai", "Faridabad", "Ghaziabad",
    "Guwahati", "Gwalior", "Indore", "Jaipur", "Jalandhar", "Jammu",
    "Jamnagar", "Jamshedpur", "Jodhpur", "Kanpur", "Kochi", "Kota",
    "Kozhikode", "Lucknow", "Ludhiana", "Madurai", "Mangaluru", "Meerut",
    "Mysuru", "Nagpur", "Nashik", "Patna", "Puducherry", "Raipur",
    "Rajkot", "Ranchi", "Salem", "Srinagar", "Surat", "Thiruvananthapuram",
    "Tiruchirappalli", "Udaipur", "Vadodara", "Varanasi", "Vijayawada",
    "Visakhapatnam"
]


class userInput(BaseModel):
   age:Annotated[int,Field(...,gt=0,lt=120,description='Age of the user')]
   weight:Annotated[float,Field(...,gt=0,description='Weight of the user')]
   height:Annotated[float,Field(...,gt=0,description='Height of the user')]
   city:Annotated[str,Field(...,description='City where the user lives')]
   income_lpa:Annotated[float,Field(...,description='Annual salary of the user')]
   occupation:Annotated[Literal['retired', 'freelancer', 'student', 'government_job',
       'business_owner', 'unemployed', 'private_job'],Field(...,description='Occupation of the user')]
   smoker:Annotated[bool,Field(...,description='Is the user a smoker')]

   @computed_field
   @property
   def bmi(self)-> float:
      return self.weight/(self.height**2)

   @computed_field
   @property
   def lifestyle_risk(self)-> str:
      if self.smoker and self.bmi >30:
         return 'high'
      elif self.smoker or self.bmi <25:
         return 'medium'
      else:
         return 'low'

   @computed_field
   @property
   def age_group(self)-> str:
      if self.age<25:
         return 'young'
      elif  self.age<45:
         return 'adult'
      elif self.age<60:
         return 'middle_age'
      return 'old'

   @computed_field
   @property
   def city_tier(self)-> int:
      if self.city in tier_1:
         return 1
      elif self.city in tier_2:
         return 2
      else:
         return 3
         
@app.post('/predict')
def predict(data:userInput):

   input_data = pd.DataFrame([{
      'bmi':data.bmi,
      'age_group':data.age_group,
      'lifestyle_risk':data.lifestyle_risk,
      'city_tier':data.city_tier,     
      'income_lpa':data.income_lpa,
      'occupation':data.occupation 
      }])

   prediction =model.predict(input_data)[0]

   return JSONResponse(status_code=200,content={'predicted_category':prediction})
