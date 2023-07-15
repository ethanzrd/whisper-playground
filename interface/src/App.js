import React, { useState, useRef, useEffect } from "react";
import { Button } from "react-bootstrap";
import withStyles from "@material-ui/core/styles/withStyles";
import Typography from "@material-ui/core/Typography";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";
import TranscribeOutput from "./TranscribeOutput";
import SettingsSections from "./SettingsSection";
import { FormHelperText } from "@material-ui/core";
import {
  MIC_SAMPLE_RATE,
  BLOCK_SIZE,
  MODEL_OPTIONS,
  SUPPORTED_LANGUAGES,
} from "./config";
import WaveformVisualizer from "./WaveformVisualizer";
import io from "socket.io-client";
import { PulseLoader } from "react-spinners";

const useStyles = () => ({
  root: {
    display: "flex",
    flex: "1",
    margin: "100px 0px 100px 0px",
    alignItems: "center",
    textAlign: "center",
    flexDirection: "column",
  },
  title: {
    marginBottom: "30px",
  },
  settingsSection: {
    marginBottom: "20px",
    display: "flex",
    width: "100%",
  },
  buttonsSection: {
    marginBottom: "40px",
  },
  recordIllustration: {
    width: "100px",
  },
});

const App = ({ classes }) => {
  const [transcribedData, setTranscribedData] = useState([]);
  const [audioData, setAudioData] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isStreamPending, setIsStreamPending] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("english");
  const [selectedModel, setSelectedModel] = useState("small");
  const [transcribeTimeout, setTranscribeTimout] = useState(5);
  const [status, setStatus] = useState("Not Recording");

  const socketRef = useRef(null);

  const audioContextRef = useRef(null);

  const streamRef = useRef(null);

  useEffect(() => {
    console.log(selectedModel);
  }, [selectedModel]);

  function b64encode(chunk) {
    // Convert the chunk array to a Float32Array
    const bytes = new Float32Array(chunk).buffer;

    // Encode the bytes as a base64 string
    let encoded = btoa(String.fromCharCode.apply(null, new Uint8Array(bytes)));

    // Return the encoded string as a UTF-8 encoded string
    return decodeURIComponent(encoded);
  }

  function handleTranscribedData(data) {
    setTranscribedData((prevData) => [...prevData, ...data]);
  }

  function startRecording() {
    setIsStreamPending(true);
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then(function (s) {
        streamRef.current = s;

        // Create a new WebSocket connection.
        socketRef.current = new io.connect("http://0.0.0.0:8000", {
          transports: ["websocket"],
        });
        const config = {
          language: selectedLanguage,
          model: selectedModel,
        };
        socketRef.current.emit("startWhispering", config);

        // When the WebSocket connection is open, start sending the audio data.
        socketRef.current.on("whisperingStarted", function () {
          setIsStreamPending(false);
          setIsRecording(true);
          audioContextRef.current = new (window.AudioContext ||
            window.webkitAudioContext)({
            sampleRate: MIC_SAMPLE_RATE,
          });
          var source = audioContextRef.current.createMediaStreamSource(
            streamRef.current
          );
          var processor = audioContextRef.current.createScriptProcessor(
            BLOCK_SIZE,
            1,
            1
          );
          source.connect(processor);
          processor.connect(audioContextRef.current.destination);

          processor.onaudioprocess = function (event) {
            var data = event.inputBuffer.getChannelData(0);
            setAudioData(new Float32Array(data));

            console.log("Sending audio chunk");
            socketRef.current.emit("audioChunk", b64encode(data));
          };
        });

        socketRef.current.on(
          "transcriptionDataAvailable",
          (transcriptionData) => {
            handleTranscribedData(transcriptionData);
          }
        );
      })
      .catch(function (error) {
        console.error("Error getting microphone input:", error);
      });
  }

  function stopRecording() {
    setIsStreamPending(true);
    socketRef.current.emit("stopWhispering");
    streamRef.current.getTracks().forEach((track) => track.stop());
    audioContextRef.current.close();
    setAudioData([]);
    socketRef.current.on("whisperingStopped", function () {
      setIsStreamPending(false);
      setIsRecording(false);
      socketRef.current.disconnect();
    });
  }

  return (
    <div className={classes.root}>
      <div className={classes.title}>
        <Typography variant="h3">
          Whisper Playground{" "}
          <span role="img" aria-label="microphone-emoji">
            🎤
          </span>
        </Typography>
      </div>
      <div className={classes.settingsSection}>
        <SettingsSections
          disabled={isRecording}
          possibleLanguages={SUPPORTED_LANGUAGES}
          selectedLanguage={selectedLanguage}
          onLanguageChange={setSelectedLanguage}
          modelOptions={MODEL_OPTIONS}
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
        />
      </div>
      <div className={classes.buttonsSection}>
        {!isRecording && (
          <Button
            onClick={startRecording}
            disabled={isStreamPending}
            variant="primary"
          >
            Start transcribing
          </Button>
        )}
        {isRecording && (
          <Button
            onClick={stopRecording}
            variant="danger"
            disabled={isStreamPending}
          >
            Stop
          </Button>
        )}
      </div>
      <div>
        <WaveformVisualizer audioData={audioData} />
      </div>

      <div>
        <TranscribeOutput transcribedData={transcribedData} />
        <PulseLoader
          sizeUnit={"px"}
          size={20}
          color="purple"
          loading={isStreamPending}
        />
      </div>
    </div>
  );
};

export default withStyles(useStyles)(App);
