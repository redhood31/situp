
const CircularProgressBar = ({ value }) => {
  return (
    <div style={{width : '100%', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
   
   <div>
        Video is processing
     </div>
   <div> 
        <progress className="progress progress-success w-56" value={value} max="100"></progress>
    
    </div>
    
    <div>
     {value.toFixed(2)} %
     </div>
     
     </div>
  );
};


export default CircularProgressBar;