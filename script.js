const { exec } = require('child_process');
const inputFile = 'historical.mp3';
const outputFile = `${inputFile}_cropped.mp3`;

// FFmpeg command to trim from 5 seconds to the end
const command = `ffmpeg -y -ss 23 -i "${inputFile}" -acodec copy "${outputFile}"`;

exec(command, (error, stdout, stderr) => {
  if (error) {
    console.error(`Error trimming audio: ${error.message}`);
    return;
  }
  if (stderr) {
    console.log(`FFmpeg stderr: ${stderr}`);
  }
  console.log(`Audio cropped from 5s to end. Saved as ${outputFile}`);
});
