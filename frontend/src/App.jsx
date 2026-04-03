import {default as api, API_BASE_URL} from "./api/api.js";
import {useEffect, useState} from "react";
import Loading from "./components/Loading.jsx";

export default function App() {
    const [connected, setConnected] = useState(false);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const ping = async () => {
            try{
                setLoading(true);
                await api.get("/health");
                setConnected(true);
                setError(null);
            }catch(e){
                setConnected(false);
                setError(e?.response?.data?.message || e);
            }finally {
                setLoading(false);
            }
        }
        ping();
    }, [])

    if (loading) return <Loading />;

    return (
        <>
            <div>Hello World</div>
            <div>Backend api url: {API_BASE_URL}</div>
            <div>Backend status: {connected ? "connected" : `can not connected. Error: ${error}`}</div>
        </>
    )
}
