import { useState} from 'react';
import './App.css';
import MapSelector from "./Components/MapSelector.tsx";
import type { LatLng } from './Interfaces.tsx';
import { CreatableMultiSelect, type Option } from './Components/CreatableMultiSelect.tsx';
import { defaultJyotishSchools, defaultRemedyCategories } from './config.tsx';
import axios from 'axios';
import ReportEditor from './Components/ReportEditor.tsx';

function App() {
  const [day, setDay] = useState<string>("");
  const [month, setMonth] = useState<string>("");
  const [year, setYear] = useState<string>("");
  const [hours, setHours] = useState<string>("");
  const [minutes, setMinutes] = useState<string>("");
  
  const [latitude, setLatitude] = useState<number>(0);
  const [longitude, setLongitude] = useState<number>(0);

  const [incRemedyCategories, setIncRemedyCategories] = useState<readonly Option[]>([]);
  const [excRemedyCategories, setExcRemedyCategories] = useState<readonly Option[]>([]);
  const [jyotishSchools, setJyotishSchools] = useState<readonly Option[]>([]);

  const [language, setLanguage]=useState<string>("");

  const [loading, setLoading]=useState<boolean>(false);

  const [kundliImageSrc,setKundliImageSrc]=useState<string | null>(null);

  const [gocharImageSrc,setGocharImageSrc]=useState<string | null>(null);

  const [reportContent, setReportContent]=useState<string>("");

  const isFormInvalid = !year || !month || !day || !hours || !minutes || !latitude || !longitude || loading;

  const handleNumberInput = (
    value: string, 
    setter: (val: string) => void, 
    min: number, 
    max: number
  ) => {
    if (value === "") {
      setter(value);
      return;
    }

    const numValue = parseInt(value, 10);
    
    if (!isNaN(numValue) && numValue >= min && numValue <= max) {
      setter(value);
    }
  };

  const handleYearInput = (val: string) => {
    if (val === "") {
        setYear(val);
        return;
    }
    const num = parseInt(val, 10);
    if (!isNaN(num) && num >= 0 && val.length <= 4) {
        setYear(val);
    }
  };

  const handleLocationUpdate = (location: LatLng) => {
    setLatitude(location.lat);
    setLongitude(location.lng);
  };

  const handleGenerateReport = async () => {
    // Basic Client-side check before sending
    if (!year || !month || !day || !hours || !minutes || !latitude || !longitude) {
      alert("Please fill in all date and time fields.");
      return;
    }
    const birth_details={
      year: parseInt(year, 10),
      month: parseInt(month, 10),
      day: parseInt(day, 10),
      hours: parseInt(hours, 10),
      minutes: parseInt(minutes, 10),
      latitude: Number(latitude),
      longitude: Number(longitude),
    };
    
    const analysis_payload = {
      ...birth_details,
      jyotish_schools: jyotishSchools.map(opt => opt.value),
      inc_remedy_categories: incRemedyCategories.map(opt => opt.value),
      exc_remedy_categories: excRemedyCategories.map(opt => opt.value),
      language: language
    };

    try {
      setLoading(true);
      const kundliResponse = await axios.post('http://localhost:5000/generate-kundli', birth_details, {responseType:'blob'});
      setKundliImageSrc(URL.createObjectURL(kundliResponse.data));

      const gocharResponse = await axios.post('http://localhost:5000/generate-gochar', birth_details, {responseType:'blob'});
      setGocharImageSrc(URL.createObjectURL(gocharResponse.data));

      const analysisResponse = await axios.post('http://localhost:5000/generate-prompt', analysis_payload);
      console.log("Report Generated:", analysisResponse.data);
      setReportContent(analysisResponse.data.analysis_result);
      setLoading(false);
      alert("Report Request Sent!");
    } catch (error) {
      console.error("Error generating report:", error);
      alert("Failed to generate report.");
    }
  };

  return (
    <>
      <input 
        type="number" 
        placeholder="Day (1-31)" 
        value={day} 
        onChange={(e) => handleNumberInput(e.target.value, setDay, 1, 31)} 
        min="1" max="31"
      />

      <input 
        type="number" 
        placeholder="Month (1-12)" 
        value={month} 
        onChange={(e) => handleNumberInput(e.target.value, setMonth, 1, 12)} 
        min="1" max="12"
      />

      <input 
        type="number" 
        placeholder="Year" 
        value={year} 
        onChange={(e) => handleYearInput(e.target.value)} 
      />

      <input 
        type="number" 
        placeholder="Hour (0-23)" 
        value={hours} 
        onChange={(e) => handleNumberInput(e.target.value, setHours, 0, 23)} 
        min="0" max="23"
      />

      <input 
        type="number" 
        placeholder="Minute (0-59)" 
        value={minutes} 
        onChange={(e) => handleNumberInput(e.target.value, setMinutes, 0, 59)} 
        min="0" max="59"
      />

      <MapSelector onLocationSelect={handleLocationUpdate}/>

      <CreatableMultiSelect 
        value={incRemedyCategories} 
        onChange={setIncRemedyCategories} 
        placeholder='Remedy categories to Include' 
        defaultOptions={defaultRemedyCategories}
      />
      
      <CreatableMultiSelect 
        value={excRemedyCategories} 
        onChange={setExcRemedyCategories} 
        placeholder='Exclude these categories' 
        defaultOptions={defaultRemedyCategories}
      />
      
      <CreatableMultiSelect 
        value={jyotishSchools} 
        onChange={setJyotishSchools} 
        placeholder='Use these jyotish schools' 
        defaultOptions={defaultJyotishSchools}
      />

      <input 
        type="input" 
        placeholder="Enter Report Language" 
        value={language} 
        onChange={(e) => setLanguage(e.target.value)}
      />
      <button onClick={handleGenerateReport} disabled={isFormInvalid}>
          {loading ? "Generating..." : "Generate Report"}
      </button>
      {gocharImageSrc && (
          <img 
            src={gocharImageSrc} 
            alt="Gochar Phal" 
            style={{ maxWidth: '100%', height: 'auto' }} 
          />
      )}
      {kundliImageSrc && (
          <img 
            src={kundliImageSrc} 
            alt="Kundli Chart" 
            style={{ maxWidth: '100%', height: 'auto' }} 
          />
      )}
      {reportContent && (
        <div>
          <ReportEditor initialText={reportContent} />
        </div>
      )}
    </>
  )
}

export default App;