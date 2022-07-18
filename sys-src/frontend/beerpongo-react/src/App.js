import './App.css';
import GameMenu from './components/GameMenu';
import GamePage from "./components/GamePage";
import {BrowserRouter, Route, Routes} from "react-router-dom";
import {UserContext} from "./context/UserContext";
import {useState} from "react";


function App() {
    const [userID, setUserID] = useState(-1);
    const [gameID, setGameID] = useState(-1);
    const value = {userID, setUserID, gameID, setGameID};
    return (
      <BrowserRouter>
          <UserContext.Provider value={value}>
            <Routes>
              <Route exact path='/' element={<GameMenu/>}/>
              <Route exact path='/game/:id' element={<GamePage/>}/>
            </Routes>
          </UserContext.Provider>
      </BrowserRouter>
  );
}

export default App;
