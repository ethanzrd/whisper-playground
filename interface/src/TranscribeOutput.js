import React from "react";
import withStyles from "@material-ui/core/styles/withStyles";
import Typography from "@material-ui/core/Typography";

const useStyles = () => ({
  root: {
    maxWidth: "800px",
    display: "flex",
  },
  outputText: {
    marginLeft: "8px",
    color: "#ef395a",
  },
});

function generateTranscriptionString(transcribedData) {
  let result = "";
  let currentSpeaker = -1;
  console.log(transcribedData);
  for (let i = 0; i < transcribedData.length; i++) {
    const currentSegment = transcribedData[i];
    const [speaker, text] = [currentSegment.speaker, currentSegment.text];
    const speakerName =
      speaker === -1 ? "Unknown Speaker" : `Speaker ${speaker + 1}`;

    if (currentSpeaker !== speaker) {
      if (result.length > 0) {
        result += "\n\n";
      }

      result += `${speakerName}: ${text}`;
      currentSpeaker = speaker;
    } else {
      result += ` ${text}`;
    }
  }

  return result;
}

const TranscribeOutput = ({ classes, transcribedData }) => {
  if (transcribedData.length === 0) {
    return <Typography variant="body1">...</Typography>;
  }

  return (
    <div className={classes.root}>
      <Typography variant="body1">
        {generateTranscriptionString(transcribedData)}
      </Typography>
    </div>
  );
};

export default withStyles(useStyles)(TranscribeOutput);
