import { createContext } from "react";

export const UserContext = createContext({
    userID: -1,
    setUserID: (prevState) => {},
    gameID: -1,
    setGameID: (prevState) => {}
});