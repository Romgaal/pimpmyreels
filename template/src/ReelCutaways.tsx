import React from 'react';
import {AbsoluteFill, Img, OffthreadVideo, Sequence, staticFile} from 'remotion';
import {Gif} from '@remotion/gif';
import mapping from '../mapping.json';

// Style rules baked in (see skills/pimp/references/style-rules.md):
// hard cuts only — NO transitions, NO zoom, NO shadow, NO text overlays.
type Seg = {
	start: number;
	end?: number;
	type?: string;
	image?: string;
	images?: string[];
	format?: string;
	align?: string;
};

const Media: React.FC<{src: string; style: React.CSSProperties}> = ({src, style}) =>
	src.toLowerCase().endsWith('.gif') ? (
		<Gif src={staticFile(src)} style={style} fit="cover" />
	) : (
		<Img src={staticFile(src)} style={style} />
	);

const ImgCut: React.FC<{seg: Seg; top: number}> = ({seg, top}) => {
	const square = seg.format === 'square';
	const w = square ? Math.round(mapping.width * 0.435) : Math.round(mapping.width * 0.519);
	const h = square ? w : Math.round(w * 0.575);
	const justify =
		seg.align === 'left' ? 'flex-start' : seg.align === 'right' ? 'flex-end' : 'center';
	return (
		<div
			style={{
				position: 'absolute',
				top: square ? top - 12 : top,
				left: 0,
				right: 0,
				display: 'flex',
				justifyContent: justify,
				paddingLeft: seg.align === 'left' ? 64 : 0,
				paddingRight: seg.align === 'right' ? 64 : 0,
			}}
		>
			<div style={{width: w, height: h, borderRadius: 10, overflow: 'hidden'}}>
				<Media
					src={seg.image as string}
					style={{width: '100%', height: '100%', objectFit: 'cover'}}
				/>
			</div>
		</div>
	);
};

const Collage: React.FC<{images: string[]}> = ({images}) => (
	<div
		style={{
			position: 'absolute',
			top: 44,
			left: 40,
			right: 40,
			display: 'grid',
			gridTemplateColumns: 'repeat(3, 1fr)',
			gap: 8,
		}}
	>
		{images.slice(0, 6).map((im, i) => (
			<div
				key={i}
				style={{height: Math.round(mapping.height * 0.107), borderRadius: 8, overflow: 'hidden'}}
			>
				<Media src={im} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
			</div>
		))}
	</div>
);

export const ReelCutaways: React.FC = () => {
	const segs = mapping.segments as Seg[];
	const top = (mapping as {imageTop?: number}).imageTop ?? 118;
	return (
		<AbsoluteFill style={{backgroundColor: '#000'}}>
			<OffthreadVideo src={staticFile(mapping.rush)} />
			{segs.map((seg, i) => {
				const end = seg.end ?? segs[i + 1]?.start ?? mapping.durationInFrames;
				return (
					<Sequence key={i} from={seg.start} durationInFrames={end - seg.start}>
						{seg.type === 'collage' ? (
							<Collage images={seg.images as string[]} />
						) : (
							<ImgCut seg={seg} top={top} />
						)}
					</Sequence>
				);
			})}
		</AbsoluteFill>
	);
};
