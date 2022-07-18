import {useContext} from "react";
import {UserContext} from "../context/UserContext";
import {useNavigate} from "react-router-dom";
import tryCreatingGame, {tryJoiningGame} from "../model/GameConnectionController";

//missing CSS
function GameMenu() {
    const {userID, setUserID, gameID, setGameID} = useContext(UserContext);

    let navigate = useNavigate();
    let _gameId;
    const joinGame = () =>{
        let path = "game/" + _gameId;
        navigate(path);
    };

    return (
        <div>
            <div>
                <input
                    type="text"
                    name="gameid"
                    onChange={(e) => {
                        setGameID(e.target.value);
                        }}>
                 </input>
                <button onClick={() => {
                        tryJoiningGame(gameID).then((result)=>{
                            console.log(result.body.playerid);
                            setUserID(result.body.playerid);
                            _gameId = gameID;
                            joinGame();
                        }); }}>
                    Join Game
                </button>
            </div>

            <div>
                <button
                    onClick={() => {
                            tryCreatingGame().then((result)=>{
                                let response = JSON.parse(result.body);
                                _gameId = response['GameId'];
                                setUserID(1);
                                setGameID(_gameId);
                                joinGame();
                            });
                        }
                    }>
                    Create Game
                </button>
            </div>
        </div>
     );
}



export default GameMenu;