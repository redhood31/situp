import logo from './logo.svg';
import './App.css';
import {useState, useEffect, useRef} from "react"
import React from "react"
import Vid from './Vid.tsx'
import {BACKEND, WEBSOCKET} from './utils.js'
import VideoPlayer from './VideoPlayer.tsx'
import axios from 'axios'
import useGetRecords from './hooks/useGetRecords.tsx'



function Player({name}){
    const [url, setUrl] = useState('')
    const [angle, setAngle] = useState(0.0)
    const [reps, setReps] = useState(0)
    const [interval, setInterval] = useState(0.0)
    const [realTime, setRealTime] = useState(true)
    const ref = useRef(0);
    const [sockets, setSockets] = useState([])

    const [recordAngle, recordInterval, recordReps, setRecordsUrl, onSeek] = useGetRecords();

    const chooseRef = useRef()

    const startIt = ()=>{
        if(localStorage.getItem(name) != null && localStorage.getItem(name) != undefined && localStorage.getItem(name) != 'undefined'){
            setSockets([])
            setAngle(0)
            setReps(0)
            setInterval(0)
            let cur_url = JSON.parse(localStorage.getItem(name))
            const parts = cur_url.split("/"); 
            joinWebsocket(parts[parts.length-1])
            setRealTime(true);
            setUrl(cur_url)
            
        }
    }
 


    const setup = async()=>{
        
    if(localStorage.getItem(name) != null && localStorage.getItem(name) != undefined && localStorage.getItem(name) != 'undefined'){
       
        let cur_url = JSON.parse(localStorage.getItem(name))
        let record_url = null;
        
        const parts = cur_url.split("/"); 
    
        try{
            // alert("Im here")
            const res = await axios.get(`${BACKEND}/check/${parts[parts.length-1]}`);

            console.log("THE RESULT OF CHECK I S " ,res.data)
            if(res.data.processed == 'true'){
                console.log(" IS TRUE");

                cur_url = `${BACKEND}/videos/static/processed${parts[parts.length-1]}`;
                record_url = `${BACKEND}/records/${parts[parts.length-1]}`
                setRecordsUrl(record_url);
                setRealTime(false);
                return;
            }else{
                setRealTime(true);
            }
        }catch(error){
            console.log("error while doing check is ", error)
        }
        
        joinWebsocket(parts[parts.length-1])
        setUrl(cur_url)
      }
    }
    useEffect(()=>{
        if(!ref || ref.current == 1){
            return;
        }
        ref.current = 1;
        setup();

    
    } , [])
    const [file, setSelectedFile] = useState('');
    const handleFileChange = (event) => {
      // Get the selected file from the input element
      const file = event.target.files[0];
      setSelectedFile(file);
    };
    const joinWebsocket = (filename) => {
        console.log("trying to connect websocket " , filename)
        const ws = new WebSocket(`${WEBSOCKET}/ws/${filename}`);
        console.log("we connected")
    // Listen for messages from the WebSocket server
        ws.onmessage = event => {
            const message = JSON.parse(event.data);

            for(let rep of message){
                setAngle(ang=>ang+rep.angle)
                setReps(rep=>rep+1)
                setInterval(intt=>intt+rep.interval)
            }

            console.log(" WEBSOCKET " , message)
        };
        ws.onerror = error => {
            console.error('WebSocket error:', error);
        };
        setSockets(prevSockets => [...prevSockets, ws]);
    }
    useEffect(()=>{
      if(file != ''){
          const formData = new FormData()
          formData.append('file', file)
          setUrl('');
        fetch(`${BACKEND}/upload`, {
            method : 'POST',
            body : formData
          }).then(response=>{
            if(!response.ok){
                throw new Error('Network response was not ok.')
            }
            return response.json();
        }).then(data=>{
            console.log("RESPONSE IS " , data)
            localStorage.setItem(name, JSON.stringify(`${BACKEND}/video/`+data.filename))
            startIt()
          }).catch(error => console.log("error while uploading a vid " , error))
      }
      return ()=>{
        for(socket in sockets)
            socket.close()
      }
    } , [file]);




    return <div style={{width: '90%', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '0% 10%',  fontSize: '20px', background: '#DCEAED'}}>
      <p style={{fontSize: '40px', marginBottom: '20px'}}> {name} </p>
    
      {realTime == true ? <Vid url={url} /> : <VideoPlayer url={url} onSeek={onSeek} />}
      
      
      <input ref={chooseRef} style={{display: 'none'}} type="file" onChange={handleFileChange} />

        <div style={{width: '100%', position: 'relative', display: 'flex',  marginTop: '30px',  height: '25px'}}>
            <div style={{position: 'absolute', left: 0, flexShrink: 0}}>
                 Average Minimum back to thigh angle
            </div>
            <div style={{position: 'absolute', right: 0, flexShrink: 0}}>
            {realTime == true ? angle/(reps==0?1:reps) :  recordAngle/(recordReps==0?1:recordReps)}
            </div>
            
        </div>
        <div style={{width: '100%', position: 'relative',  display: 'flex',  marginTop: '5px',  height: '25px'}}>
            <div style={{position: 'absolute', left: 0}}>
            Average Speed of excercise
            </div>
            <div style={{position: 'absolute', right: 0}}>
            {realTime == true ? interval/(reps==0?1:reps) : recordInterval/(recordReps==0?1:recordReps)}
            </div>
            
        </div>
        <div style={{width: '100%', position: 'relative',  display: 'flex', marginTop: '5px', height: '25px'}}>
            <div style={{position: 'absolute', left: 0}}>
                Repetitions
            </div>
            <div style={{position: 'absolute', right: 0}}>
                {realTime == true ? reps : recordReps}
            </div>
            
        </div>

        <div style={{width: '100%', position: 'relative',  display: 'flex', height: '40px', marginTop: '40px', justifyContent: 'center'}}>
        
        <button className="btn btn-accent" onClick={(e)=>{chooseRef.current.click()}}>Upload file</button>
        <button className="btn btn-primary ml-4" onClick={(e)=>{let sv=url; setUrl(''); setTimeout(()=>setUrl(sv), 200)}}>Start over</button>

        </div>
    </div> 

}

export default Player;