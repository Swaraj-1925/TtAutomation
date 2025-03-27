import { useState } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import InputFom from "./components/Input_form.jsx";
import Home from "./components/home.jsx";

function App() {
  const [count, setCount] = useState(0)

  return (
      <BrowserRouter>
          <Routes>
              <Route path="/" element={<InputFom/>}/>
              <Route path="/home" element={<Home />} />
          </Routes>
      </BrowserRouter>

  )
}

export default App
