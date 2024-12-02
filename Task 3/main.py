from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

grid_data = [
    {"id": i+1, "column1": f"Row {i+1} Data 1", "column2": f"Row {i+1} Data 2", 
     "column3": f"Row {i+1} Data 3", "column4": f"Row {i+1} Data 4", "column5": f"Row {i+1} Data 5"}
    for i in range(20)
]

@app.get("/api/grid", response_model=List[dict])
def get_grid():
    return grid_data
