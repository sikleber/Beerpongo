import axios from 'axios'
import {GET_GAME_URL, POST_GAME_URL, PUT_GAME_URL, JOIN_GAME_URL} from "../constants/BackendUrl";


export function tryJoiningGame(gameId) {
  const url = JOIN_GAME_URL.replace("{GAME_ID}", gameId)
    return new Promise((resolve)=>{
        axios.get(url)
            .then(response => {
                console.log("Try joining Game received: ", response);
                resolve(response.data);
            }).catch(err => {
            console.error(err);
            throw Error("Trying to join game with Id: " + gameId + "failed!");
        })
    });
}

export function tryGettingGame(gameId) {
  const url = GET_GAME_URL.replace("{GAME_ID}", gameId);
  return new Promise((resolve)=>{
      axios.get(url)
          .then(response => {
              console.log("Try getting game received: ", response);
              resolve(response.data);
          }).catch(err => {
          console.error(err)
          throw Error("Get joining game failed");
      })
  })
}

export default function tryCreatingGame() {
    return new Promise((resolve)=> {
        axios.post(POST_GAME_URL).then(response => {
            console.log("Try creating game received: ", response);
            resolve(response.data);
        }).catch(err => {
            console.error(err)
            throw Error("Post creating game failed");
        })
    });
}

export function tryUpdatingGame(gameId, gameUpdate) {
  let data = {
    "id": gameId,
    "state": gameUpdate
  }
  return new Promise((resolve)=>{
      axios.put(PUT_GAME_URL, data)
          .then(response => {
              console.log("Try updating game received: ", response);
              resolve(response.data);
          }).catch(err => {
          console.error(err)
          throw Error("Put updating game failed");
      })
  });
}

