import axios from 'axios'
import tryCreatingGame, {tryUpdatingGame, tryGettingGame, tryJoiningGame} from "./GameConnectionController";

jest.mock('axios');


describe('tryGettingGame', () => {
    it('should return correct data', () => {
        let mockedResponse =  {
            config: {
                timeout: 0, 
                xsrfCookieName: "XSFR-TOKEN"
            },
            data:{
                "statusCode": "200",
                "body": {
                    "GameId": "1234ABC",
                    "State": "1:X",
                    "playerCount": 1
                },
            },      
            headers:{
                "content-length":"64",
                "content-type":"application/json"

            },
            status:200,
            statusText:"OK"
        };
        axios.get = jest.fn().mockResolvedValue(mockedResponse);

        tryGettingGame("1234ABC").then(response => {
            expect(response).toEqual(mockedResponse.data);
        })
        
    })
    /*
    it('Error, if getting game fails', () => {
        const message = "Get joining game failed"
        
        axios.get = jest.fn().mockRejectedValue(message)

        tryGettingGame("ABCD56").then(response => {
            expect(response).toThrow();
        })
        //expect(() => tryGettingGame("1")).toThrow(message);
        
    })*/
})

/
describe('tryJoiningGame', () => {
    it('should return correct data', () => {
        let mockedResponse =  {
            config: {
                timeout: 0, 
                xsrfCookieName: "XSFR-TOKEN"
            },
            data:{
                "statusCode": "200",
                "body": {
                    "id": "1234ABC",
                    "playerid": 2
                },
            },      
            headers:{
                "content-length":"64",
                "content-type":"application/json"

            },
            status:200,
            statusText:"OK"
        };

        axios.get = jest.fn().mockResolvedValue(mockedResponse);

        tryJoiningGame("1234ABC").then(response => {
            expect(response).toEqual(mockedResponse.data);
        })
    })
})

describe('tryCreatingGame', () => {
    it('should return correct data', () => {
        let mockedResponse =  {
            config: {
                timeout: 0, 
                xsrfCookieName: "XSFR-TOKEN"
            },
            data:{
                "statusCode": "200",
                "body": {
                    "id": "9876YZ",
                    "playerid": 1
                },
            },      
            headers:{
                "content-length":"64",
                "content-type":"application/json"

            },
            status:200,
            statusText:"OK"
        };

        axios.post = jest.fn().mockResolvedValue(mockedResponse);

        tryCreatingGame().then(response => {
            expect(response).toEqual(mockedResponse.data);
        })
    })
})

describe('tryUpdatingGame', () => {
    it('should return correct data', () => {
        let mockedResponse =  {
            config: {
                timeout: 0, 
                xsrfCookieName: "XSFR-TOKEN"
            },
            data:{
                "statusCode": "200",
                "body": "{message: Game State of Game 9876YZ updated}"
            },      
            headers:{
                "content-length":"64",
                "content-type":"application/json"
            },
            status:200,
            statusText:"OK"
        };

        axios.put = jest.fn().mockResolvedValue(mockedResponse);

        tryUpdatingGame("9876YZ", "1:31").then(response => {
            expect(response).toEqual(mockedResponse.data);
        })
    })
})

    