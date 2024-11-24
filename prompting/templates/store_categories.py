import os
from dotenv import load_dotenv

# for mongo
from pymongo import MongoClient

load_dotenv()

cluster = MongoClient(os.getenv("DATABASE_CONNECTION"))
db = cluster['llm-maritime-risk']

def store_current_categories():
    data = [
        {
            "_id": 1,
            "Category": "Vessel Delay",
            "Description": "Delays in vessel schedules affecting port operations and shipping timelines."
        },
        {
            "_id": 2,
            "Category": "Vessel Accidents",
            "Description": "Accidents involving vessels, impacting safety, cargo, and port operations."
        },
        {
            "_id": 3,
            "Category": "Maritime Piracy/Terrorism Risk",
            "Description": "Risks from piracy or terrorism targeting vessels, cargo, or routes.",
        },
        {
            "_id": 4,
            "Category": "Port or Important Route Congestion",
            "Description": "Congestion at ports or critical routes, delaying vessel movement.",
        },
        {
            "_id": 5,
            "Category": "Port Criminal Activities",
            "Description": "Illegal activities at ports, impacting security and cargo safety.",
        },
        {
            "_id": 6,
            "Category": "Cargo Damage and Loss",
            "Description": "Loss or damage to cargo during transportation or handling processes.",
        },
        {
            "_id": 7,
            "Category": "Inland Transportation Risks",
            "Description": "Risks in land transport affecting cargo or vessel schedules.",
        },
        {
            "_id": 8,
            "Category": "Environmental Impact and Pollution",
            "Description": "Pollution or environmental damage caused by maritime activities or spills.",
        },
        {
            "_id": 9,
            "Category": "Natural Extreme Events and Extreme Weather",
            "Description": "Severe weather or natural events affecting maritime routes or ports.",
        },
        {
            "_id": 10,
            "Category": "Cargo or Ship Detainment",
            "Description": "Cargo or vessels detained due to inspections, regulations, or disputes.",
        },
        {
            "_id": 11,
            "Category": "Unstable Regulatory and Political Environment",
            "Description": "Political instability or regulatory changes affecting maritime operations.",
        },
        {
            "_id": 12,
            "Category": "Others",
            "Description": "Maritime events outside predefined categories requiring separate classification.",
        },
        {
            "_id": 13,
            "Category": "Not maritime-related",
            "Description": "Events unrelated to maritime activities or not impacting the maritime sector."
        }
    ]

    for item in data:
        update_obj = {
            "$set": {
                "Category": item["Category"],
                "Description": item["Description"]
            }
        }
        db['Risk_Categories'].update_one({"_id": item["_id"]}, update_obj, upsert=True)


if __name__ == "__main__":
    store_current_categories()