import logo from './logo.svg';
import './App.css';
import {useState, useEffect, useRef} from "react"
import React from "react"
function Vid({url, upload}){

    useEffect(()=>{
        alert('hey hey');
    }, [])
    return <span className={`${url == '' ? 'loading loading-bars loading-lg text-accent' : ''}`}>
        
        
    <iframe
    style={{width: '640px', height: '360px', background: '#D9D9D9'}}
    src={url}
    allow="accelerometer, autoplay; encrypted-media; gyroscope; picture-in-picture"
    allowFullScreen 
    
    > 
    </iframe>
    
    </span>

}

export default Vid;