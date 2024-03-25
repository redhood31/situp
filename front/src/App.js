import logo from './logo.svg';
import './App.css';
import {useState, useEffect, useRef} from "react"
import Vid from './Vid.tsx'
import Player from './Player2.tsx'
function App() {
  const [imageSrc, setImageSrc] = useState('');
    const isValidBase64 = (str) => {
      try {
         console.log("valid\n")
          window.atob(str);
          return true;
      } catch (e) {
          return false;
      }
  };
  const ref = useRef(0)

  // return <img src={imageSrc} alt="Video Stream" />;
  


  return  <>
  <div style={{minHeight: '12vh', width:'100%', display: 'flex', justifyContent: 'center', alignItems: 'center', fontSize: '40px'}}> Pose recognition</div>
  
  <div style={{width: '100%', height: '88vh', display: 'flex',  background: '#DCEAED'}}>
  
    <div style={{width: '50%', height: '100%', display: 'flex', flexSrhink: 0, borderRight: '2.5px solid #B9DDE5'}}> 
      <Player name="Expert Video Save" />
    </div>

    <div style={{width: '50%', height: '100%', display: 'flex', flexShrink: 0, borderLeft: '2.5px solid #B9DDE5'}}> 
      <Player name="Live feed Save" />
    </div>
  </div>
  </>
}

export default App;
