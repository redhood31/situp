import logo from './logo.svg';
import './App.css';
import {useState, useEffect, useRef} from "react"
import React from "react"
import ReactPlayer from 'react-player';
import mux from "mux-embed";
function VideoPlayer({url, onSeek}){
    useEffect( ()=>{
        // alert("ITs VIDEO Player")
    }, [])

    const videoRef = useRef(null);

    const handleProgress = (state) => {
        // if (!playing) {
        //   setPlaying(true);
        // }
        setPlayed(state.played);
      };

      const [duration, setDuration] = useState(0);
      const [played, setPlayed] = useState(0);
    const handleDuration = (duration) => {
        setDuration(duration);
      };
    const [curSec, setCurSec] = useState(0);
    const cur = useRef(0);
    return (
        
    <ReactPlayer 
    width="640" 
    height="360"
    ref={videoRef}
    controls={true}
    url={url}
    onSeek={(secs)=>{
        console.log("SEC " , secs, ' ' , cur.current)
        if(secs != cur.current){
            videoRef.current.seekTo(secs)
            cur.current = secs;
        }
    }}
    onPlaybackRateChange={()=>{alert("OnPlaybackRateChange")}}
    // onProgress={handleProgress}
    // onDuration={handleDuration}
    
    >
          {/* <source src={url} type="video/mp4" />
          Your browser does not support the video tag. */}
    </ReactPlayer>

    )
    
    

}




export default VideoPlayer;