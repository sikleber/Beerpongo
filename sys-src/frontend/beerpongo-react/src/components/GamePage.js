import Field from "./Field";
import React from "react";
import {Link} from "react-router-dom";
import {UserContext} from "../context/UserContext";
import {tryUpdatingGame, tryGettingGame} from "../model/GameConnectionController";



class GamePage extends React.Component{

    static contextType = UserContext;
    invalidContext;
    defaultUpdateString;
    gameID;

    componentDidMount() {
        if(this.invalidContext) return;
        let {userID, setUserID, gameID, setGameID} = this.context;
        this.gameID = gameID;
        tryGettingGame(gameID).then((result) => {
            this.defaultUpdateString = userID + ":X";
            let gameString = result.body.State;
            let _activePlayer = this.CheckActivePlayer(gameString, userID);

            let _state = {
                gameId: gameID,
                userId: userID,
                updateString: this.defaultUpdateString,
                gameString: gameString,
                activePlayer: _activePlayer
            };
            this.timerID = setInterval(
                () => this.tick(),
                10000
            );
            this.setState(_state);
        });
    }

    componentWillUnmount() {
        if(this.timerID === undefined) return;
        clearInterval(this.timerID);
    }

    tick(){
        // check if we are the active player or not
        if(this.state.activePlayer === false){
            // we need to update the game
            tryGettingGame(this.gameID).then((result) => {
                let _shallowState = this.state;
                _shallowState.gameString = result.body.State;
                _shallowState.activePlayer = this.CheckActivePlayer(_shallowState.gameString, _shallowState.userId);
                this.setState(_shallowState);
            });
        }
    }

    resetUpdateString(){
        tryGettingGame(this.gameID).then((result) => {
            let _shallowState = this.state;
            _shallowState.gameString = result.body.State;
            _shallowState.updateString = _shallowState.userId + ":X";
            _shallowState.activePlayer = this.CheckActivePlayer(_shallowState.gameString, _shallowState.userId);
            this.setState(_shallowState);
        });
    }

    CheckActivePlayer(gameString, userID){
        if(userID >= 3) return false;

        let _activePlayer = false;
        if(gameString.length > 0) {
            let splits = gameString.split(',');
            if (!splits[splits.length - 1].startsWith(userID)) {
                _activePlayer = true;
            }
        }else{
            // The player who has created the game is always the first player.
            if(userID == 1){
                _activePlayer = true;
            }
        }
        return _activePlayer;
    }

    cupClicked(cup){
        // check if we have to add or remove the cup
        // simple check if the updateString contains the cup
        let cups = "";
        let _shallowState = this.state;
        if(_shallowState.updateString.length > _shallowState.userId.toString().length + 1){
            cups = _shallowState.updateString.substring(_shallowState.userId.toString().length + 1);
        }
        if(cups.includes(cup)){
            // remove
            cups = cups.replace(cup.toString(), '');
            // check if we have to add X
            if(cups.length == 0){
                cups += 'X';
            }
            _shallowState.updateString = _shallowState.updateString.substring(0, _shallowState.userId.toString().length + 1) + cups;
        }else{
            // add
            // check if we have to remove the X
            cups = cups.replace('X', '') + cup;
            _shallowState.updateString = _shallowState.updateString.substring(0, _shallowState.userId.toString().length + 1) + cups;
        }
        this.setState(_shallowState);
    }

    render() {
        // check if we have a valid context
        let {userID, setUserID, gameID, setGameID} = this.context;
        if (userID === -1 && gameID === -1){
            this.invalidContext = true;
            // return an error message
            return (
                (
                    <div>
                        <p>Use the Button "Join" and do not enter the url for a specific game!</p>
                    </div>
                )
            ) ;
        }else{
            this.invalidContext = false;
        }

        // check if state was already set
        if (this.state === null){
            return (
                <div></div>
            );
        }

        // Build op the default dictionary
        let dict = {
            // Classnames
            "p1_0_className": "cup1_unselected",
            "p1_1_className": "cup1_unselected",
            "p1_2_className": "cup1_unselected",
            "p1_3_className": "cup1_unselected",
            "p1_4_className": "cup1_unselected",
            "p1_5_className": "cup1_unselected",
            "p1_6_className": "cup1_unselected",
            "p1_7_className": "cup1_unselected",
            "p1_8_className": "cup1_unselected",
            "p1_9_className": "cup1_unselected",
            "p2_0_className": "cup2_unselected",
            "p2_1_className": "cup2_unselected",
            "p2_2_className": "cup2_unselected",
            "p2_3_className": "cup2_unselected",
            "p2_4_className": "cup2_unselected",
            "p2_5_className": "cup2_unselected",
            "p2_6_className": "cup2_unselected",
            "p2_7_className": "cup2_unselected",
            "p2_8_className": "cup2_unselected",
            "p2_9_className": "cup2_unselected",
            // On-Click-Handlers -> We do not update after every button -> it is possible to select/unselect  cup
            // during one turn more than once -> we send an update-request after finishing the turn
            // We need to allow updates only for the correct side!
            // TODO: We need to get the real player-ID's here
            "p1_0_OnClick": (this.state.userId >= 3 || this.state.userId === 2) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 0) : null),
            "p1_1_OnClick": (this.state.userId >= 3 || this.state.userId === 2) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 1) : null),
            "p1_2_OnClick": (this.state.userId >= 3 || this.state.userId === 2) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 2) : null),
            "p1_3_OnClick": (this.state.userId >= 3 || this.state.userId === 2) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 3) : null),
            "p1_4_OnClick": (this.state.userId >= 3 || this.state.userId === 2) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 4) : null),
            "p1_5_OnClick": (this.state.userId >= 3 || this.state.userId === 2) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 5) : null),
            "p1_6_OnClick": (this.state.userId >= 3 || this.state.userId === 2) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 6) : null),
            "p1_7_OnClick": (this.state.userId >= 3 || this.state.userId === 2) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 7) : null),
            "p1_8_OnClick": (this.state.userId >= 3 || this.state.userId === 2) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 8) : null),
            "p1_9_OnClick": (this.state.userId >= 3 || this.state.userId === 2) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 9) : null),
            "p2_0_OnClick": (this.state.userId >= 3 || this.state.userId === 1) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 0) : null),
            "p2_1_OnClick": (this.state.userId >= 3 || this.state.userId === 1) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 1) : null),
            "p2_2_OnClick": (this.state.userId >= 3 || this.state.userId === 1) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 2) : null),
            "p2_3_OnClick": (this.state.userId >= 3 || this.state.userId === 1) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 3) : null),
            "p2_4_OnClick": (this.state.userId >= 3 || this.state.userId === 1) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 4) : null),
            "p2_5_OnClick": (this.state.userId >= 3 || this.state.userId === 1) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 5) : null),
            "p2_6_OnClick": (this.state.userId >= 3 || this.state.userId === 1) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 6) : null),
            "p2_7_OnClick": (this.state.userId >= 3 || this.state.userId === 1) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 7) : null),
            "p2_8_OnClick": (this.state.userId >= 3 || this.state.userId === 1) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 8) : null),
            "p2_9_OnClick": (this.state.userId >= 3 || this.state.userId === 1) ? null : (this.state.activePlayer === true ? this.cupClicked.bind(this, 9) : null)
        }

        // parse the game-string and set the className for the already hit cups to selected and remove the on-click
        if(this.state.gameString.length > 0) {
            let turns = this.state.gameString.split(',');
            for (const element of turns) {
                let turn = element.split(':');
                if (turn.length === 2) {
                    let id = turn[0];
                    let hits = turn[1];
                    // TODO: later we need to decided here, which side the player with the current id is
                    let cupName;
                    let newClassName;
                    // iterate all hits
                    for(let i = 0; i < hits.length; i++){
                        let cup = hits[i];
                        cupName = undefined;
                        if (cup !== 'X' && !isNaN(parseInt(cup, 10))) {
                            if (id === "1") {
                                // now we can build the name of the cup in the field
                                cupName = "p1_" + cup;
                                newClassName = "cup1_selected";
                            } else if (id === "2") {
                                cupName = "p2_" + cup;
                                newClassName = "cup2_selected";
                            } else {
                                // invalid format
                                alert("Error during parsing the game!");
                                return <div>
                                    <p>Error!</p>
                                </div>
                            }
                        }
                        if(cupName != undefined) {
                            // update the css for the hit cup
                            dict[cupName.concat("_className")] = newClassName;
                            // no reaction in clicks
                            dict[cupName.concat("_OnClick")] = null;
                        }
                    }
                } else {
                    // invalid format
                    alert("Error during parsing the game!");
                    return <div>
                        <p>Error!</p>
                    </div>
                }
            }
        }

        // parse the update-string and change the className for the currently selected cups for this round
        // do not check the id and the colon
        for (let i = this.state.userId.toString().length + 1; i < this.state.updateString.length; i++) {
            let cupName;
            let newClassName;
            if (this.state.userId === 1) {
                cupName = "p1_" + this.state.updateString[i];
                newClassName = "cup1_unselected_clicked";

            } else {
                cupName = "p2_" + this.state.updateString[i];
                newClassName = "cup2_unselected_clicked";
            }

            // update css for the selected cup
            dict[cupName.concat("_className")] = newClassName;
        }

        let document = (
            <div>
                <p>ID: {this.state.gameId}</p>
                <Field dictVal={dict}/>
                <button onClick={() => {
                    tryUpdatingGame(this.state.gameId,
                        this.state.updateString).then((result)=>{
                        this.resetUpdateString();
                    });
                }}>
                    Spielzug beenden
                </button>
                {/* Quitting the game will lead the user to the game menu page */}
                <nav>
                    <Link to="/">Spiel Beenden</Link>
                </nav>
            </div>
        );

        return (
            document
        );

    }
}

export default GamePage;
