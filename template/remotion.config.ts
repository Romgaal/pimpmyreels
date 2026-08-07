import {Config} from '@remotion/cli/config';

// H.264 straight out — never render a ProRes intermediate (a 42s reel would weigh ~3GB).
Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(95);
Config.setCodec('h264');
Config.setCrf(15);
