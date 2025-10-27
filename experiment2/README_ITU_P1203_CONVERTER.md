# CSV to ITU-P1203 JSON Converter

This tool converts performance CSV files to ITU-P1203 Mode 0 JSON format.

## Features

- Converts `performance_ue{id}.csv` files to ITU-P1203 Mode 0 JSON format
- Each CSV row (1 second of data) becomes one video segment
- Automatically includes initial stalling period of 8 seconds
- No audio stream (I11 segments empty)
- Fixed video parameters: 2048x1080 resolution, h264 codec

## JSON Structure

The generated JSON follows ITU-P1203 Mode 0 format with:

- **IGen**: General parameters
  - `device`: "pc"
  - `displaySize`: "2048x1080"
  - `viewingDistance`: 0

- **I11**: Audio stream (empty - no audio considered)

- **I13**: Video stream
  - `streamId`: 42
  - `segments`: Array of video segments, each containing:
    - `bitrate`: From CSV (kbps)
    - `codec`: "h264"
    - `duration`: 1 (second)
    - `fps`: From CSV `framespersecond` field
    - `resolution`: "2048x1080"
    - `start`: Increments from 0, +1 per segment

- **I23**: Stalling events
  - `stalling`: Array of stalling events `[[start, duration], ...]`
    - Initial stalling: `[[0, 8]]` (8 seconds at start)
  - `streamId`: 42

## Usage

### Single File Conversion

```bash
python3 convert_to_itu_p1203.py <input_csv> [output_json]
```

**Example:**
```bash
python3 convert_to_itu_p1203.py data/edge2/performance_ue1.csv
# Output: data/edge2/performance_ue1_itu_p1203.json

# Custom output path:
python3 convert_to_itu_p1203.py data/edge2/performance_ue1.csv output/ue1.json
```

### Batch Conversion

Convert all `performance_ue*.csv` files in a directory:

```bash
python3 convert_to_itu_p1203.py --batch <directory>
```

**Example:**
```bash
python3 convert_to_itu_p1203.py --batch data/edge2
```

## CSV Input Format

The input CSV must have these columns:
- `bitrate`: Video bitrate in kbps
- `framespersecond`: Frame rate (fps)
- Other columns (packetlost, jitter, rtt, timestamp, server, size) are ignored

Example CSV:
```csv
bitrate,packetlost,jitter,rtt,framespersecond,timestamp,server,size
334.48,0,2,2.67,62,1761461726832.405,,
504.06,0,1,2.75,60,1761461727841.526,,
528.55,0,1,3,60,1761461728831.561,,
```

## Output Example

```json
{
  "IGen": {
    "device": "pc",
    "displaySize": "2048x1080",
    "viewingDistance": 0
  },
  "I11": {
    "segments": []
  },
  "I13": {
    "streamId": 42,
    "segments": [
      {
        "bitrate": 334.48,
        "codec": "h264",
        "duration": 1,
        "fps": 62,
        "resolution": "2048x1080",
        "start": 0
      },
      ...
    ]
  },
  "I23": {
    "stalling": [[0, 8]],
    "streamId": 42
  }
}
```

## Notes

- Each row in the CSV represents 1 second of video data
- The `start` field begins at 0 and increments by 1 for each segment
- All segments have `duration: 1` (second)
- Resolution is fixed at 2048x1080 for all segments
- Codec is fixed at h264
- One stalling event is always added at the beginning (0-8 seconds)
