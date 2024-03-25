import logo from './logo.svg';
import {useState, useEffect, useRef} from "react"
import axios from 'axios'
function useGetRecords(){
    const [url, setUrl] = useState('');
    const [data, setData] = useState();
    const [angle, setAngle] = useState(0)
    const [interval, setInterval] = useState(0)
    const [reps, setReps] = useState(0)
    const ref = useRef(null);

    useEffect(()=>{
        if(url != ref.current){
            ref.current = url;
            axios.get(url).then(res=>{
                setData(res.data);
            })
        }
    } , [url])
    
    const setRecordsUrl = (new_url)=>{
        setUrl(new_url);
    }
    const onSeek = (timestamp) => {
        let cur_int = 0;
        let cur_ang = 0;
        let cur_rep = 0;

        for(let record of data){
            if(record.time <= timestamp){
                cur_int += record.interval;
                cur_ang += record.angle;
                cur_rep += 1;
            }
        }
        setInterval(cur_int);
        setAngle(cur_ang);
        setReps(cur_rep);
    }
 
    return [angle, interval, reps, setRecordsUrl, onSeek]
}

export default useGetRecords;