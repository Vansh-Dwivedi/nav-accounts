import { BrowserRouter } from 'react-router-dom';
import './Appp.css';
import { AuthWrapper } from './auth/AuthWrapper';


function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthWrapper />
      </BrowserRouter>
    </div>
  );
}

export default App;
