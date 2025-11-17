"""Channel API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import Channel, get_db
from schemas import ChannelCreate, ChannelUpdate, ChannelResponse

router = APIRouter()

@router.post("/", response_model=ChannelResponse, status_code=201)
def create_channel(channel: ChannelCreate, db: Session = Depends(get_db)):
    db_channel = Channel(**channel.model_dump())
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel

@router.get("/", response_model=List[ChannelResponse])
def list_channels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    channels = db.query(Channel).offset(skip).limit(limit).all()
    return channels

@router.get("/{channel_id}", response_model=ChannelResponse)
def get_channel(channel_id: str, db: Session = Depends(get_db)):
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel

@router.put("/{channel_id}", response_model=ChannelResponse)
def update_channel(channel_id: str, channel_update: ChannelUpdate, db: Session = Depends(get_db)):
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    for key, value in channel_update.model_dump(exclude_unset=True).items():
        setattr(channel, key, value)
    db.commit()
    db.refresh(channel)
    return channel

@router.delete("/{channel_id}", status_code=204)
def delete_channel(channel_id: str, db: Session = Depends(get_db)):
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    db.delete(channel)
    db.commit()
