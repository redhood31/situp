import logo from './logo.svg';
import './App.css';
import {useState, useEffect, useRef} from "react"
import React from "react"
import Vid from './Vid.tsx'
import {BACKEND, WEBSOCKET} from './utils.js'
import VideoPlayer from './VideoPlayer.tsx'
import axios from 'axios'
import useGetRecords from './hooks/useGetRecords.tsx'

import CircularProgressBar from './CircularProgressBar.tsx'

function Player({name}){
    const [url, setUrl] = useState('')
    const [status, setStatus] = useState(0);
    const ref = useRef(0);
    const [sockets, setSockets] = useState([])
    const [noFile, setNoFile] = useState(false);
    const [recordAngle, recordInterval, recordReps, setRecordsUrl, onSeek] = useGetRecords();

    const chooseRef = useRef()

    const startIt = ()=>{
        if(localStorage.getItem(name) != null && localStorage.getItem(name) != undefined && localStorage.getItem(name) != 'undefined'){

            let file_name = localStorage.getItem(name)
     
            

            setUrl(`${BACKEND}/processed/${file_name}`)
            
        }
    }
 


    const setup = async()=>{
        
    if(url == '' && localStorage.getItem(name) != null && localStorage.getItem(name) !== undefined && localStorage.getItem(name) !== 'undefined' && localStorage.getItem(name) != null){
   
        let file_name = localStorage.getItem(name)

        console.log(' FILE NAME ' , file_name, file_name !== undefined)
        try{
            // alert("Im here")
            const res = await axios.get(`${BACKEND}/check-status/${file_name}`);

            console.log("THE RESULT OF CHECK I S " ,res.data)
            if(res.data.status == true){
                let video_url = `${BACKEND}/videos/static/processed_${file_name}`
                console.log("VID " , video_url)
                setNoFile(false);
                setUrl(video_url)

            

                return;
            }else{
                if(res.data.status != undefined){
                    if(res.data.status == 0){
                        setNoFile(true);
                    }else{
                        setNoFile(false);
                        setStatus(res.data.status)
                    }

                }
                setUrl('')  
            }
        }catch(error){
            console.log("error while doing check is ", error)
        }
        
   
      }
    }

    const progressBar = ()=>{
        setup();
        console.log("hey ", url)
        if(url !== '')
            return
    }
    useEffect(()=>{
        console.log("URL CHANGE")
        if(!ref)
            return
        if(ref.current == 0){
            ref.current += 1
            return
        }
        if(ref.current == 1){
            progressBar();
            ref.current += 1;
            return;
        }
        setTimeout(progressBar, 700)
    }, [url, ref, status])

    const [file, setSelectedFile] = useState('');
    const handleFileChange = (event) => {
      // Get the selected file from the input element
      const file = event.target.files[0];
      setSelectedFile(file);
    };

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
            console.log("RESPONSE IS " ,    data.filename)
            localStorage.setItem(name, data.filename)
            setStatus(0.01)
            // startIt()
          }).catch(error => console.log("error while uploading a vid " , error))
      }

    } , [file]);


    const downloadVideo = ()=>{
        if(url == ''){
            alert("Video is not yet available")
            return;
        }
        
    // Fetch the video file

    fetch(url, 
        {
            method : "GET",
            headers: {"Content-Type" : "application/json"}
        }).then(response => response.blob()).then(blob => {
            const blobUrl = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = blobUrl;
            link.download = `url`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(blobUrl);
        })
    // let vid_url = url
    // const response = await fetch(vid_url);
    // const blob = await response.blob();

    // // Create a blob URL
    // const blobUrl = URL.createObjectURL(blob);

    // // Create an anchor element
    // const link = document.createElement('a');
    

    // // Append the link to the document body and trigger the download
   
    // // Clean up
 
    }

    return <div style={{width: '90%', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '0% 10%',  fontSize: '20px', background: '#DCEAED'}}>
      <p style={{fontSize: '40px', marginBottom: '20px'}}> {name} </p>
    

      {noFile == true ? <div style={{width : "640px", height : "360px", background : '#D3D3D3', display: 'flex', justifyContent: 'center', alignItems: 'center'}}> No file is uploaded </div> : 
      (url == '' ? <div style={{width : "640px", height : "360px", background : '#D3D3D3'}}> <CircularProgressBar value={status}/> </div> : <VideoPlayer url={url} onSeek={onSeek} />)
      }
      
      
      <input ref={chooseRef} style={{display: 'none'}} type="file" onChange={handleFileChange} />

        <div style={{width: '100%', position: 'relative', display: 'flex',  marginTop: '30px',  height: '25px', display: 'none'}}>
            <div style={{position: 'absolute', left: 0, flexShrink: 0}}>
                 Average Minimum back to thigh angle
            </div>
            <div style={{position: 'absolute', right: 0, flexShrink: 0}}>
            {/* {realTime == true ? angle/(reps==0?1:reps) :  recordAngle/(recordReps==0?1:recordReps)} */}
            </div>
            
        </div>
        <div style={{width: '100%', position: 'relative',  display: 'flex',  marginTop: '5px',  height: '25px', display: 'none'}}>
            <div style={{position: 'absolute', left: 0}}>
            Average Speed of excercise
            </div>
            <div style={{position: 'absolute', right: 0}}>
            {/* {realTime == true ? interval/(reps==0?1:reps) : recordInterval/(recordReps==0?1:recordReps)} */}
            </div>
            
        </div>
        <div style={{width: '100%', position: 'relative',  display: 'flex', marginTop: '5px', height: '25px', display: 'none'}}>
            <div style={{position: 'absolute', left: 0}}>
                Repetitions
            </div>
            <div style={{position: 'absolute', right: 0}}>
                {/* {realTime == true ? reps : recordReps} */}
            </div>
            
        </div>

        <div style={{width: '100%', position: 'relative',  display: 'flex', height: '40px', marginTop: '40px', justifyContent: 'center'}}>
        
        <button className="btn btn-accent" onClick={(e)=>{chooseRef.current.click()}}>Upload file</button>
        <button className="btn btn-primary ml-4" onClick={(e)=>{downloadVideo()}}>Download processed</button>

        </div>
    </div> 

}

export default Player;