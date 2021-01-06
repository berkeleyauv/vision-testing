import argparse
import os

from perception import ALGOS
from perception.vis.FrameWrapper import FrameWrapper
import cv2 as cv
from perception.vis.Visualizer import Visualizer
import cProfile
import imageio


def run(data_sources, algorithm, save_video=False):
    out = None
    window_builder = Visualizer(algorithm.kwargs)
    data = FrameWrapper(data_sources, 0.25)
    frame_count = 0
    paused = False
    speed = 1

    while data.has_next():
        if frame_count % speed == 0 and not paused:
            frame = next(data)
            frame_count += 1

            if algorithm.kwargs:
                state, debug_frames = algorithm.analyze(frame, debug=True, slider_vals=window_builder.update_vars())
            else:
                state, debug_frames = algorithm.analyze(frame, debug=True)

            to_show = window_builder.display(debug_frames)
            cv.imshow('Debug Frames', to_show)
            if save_video:
                if out is None:
                    # height, width, _ = to_show.shape
                    # TODO: get codec to work
                    # out = cv.VideoWriter('rec.mp4', cv.VideoWriter_fourcc(*'mp4v'), 60, (height, width))
                    out = imageio.get_writer('vis_rec.mp4')
                if out:
                    out_img = cv.cvtColor(to_show, cv.COLOR_BGR2RGB)
                    out.append_data(out_img)

        key = cv.waitKey(30)
        if key == ord('q') or key == 27:
            break
        if key == ord('p'):
            paused = not paused
        if key == ord('i') and speed > 1:
            speed -= 1
            print(f'speed {speed}')
        if key == ord('o'):
            speed += 1
            print(f'speed {speed}')


    cv.destroyAllWindows()
    if out:
        out.close()


def profile(*args, stats='all'):
    with cProfile.Profile() as pr:
        run(*args)
    if stats == 'all':
        pr.print_stats()
    else:
        pr.print_stats(stats)


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Visualizes perception algorithms.')
    parser.add_argument('--data', default='webcam', type=str)
    parser.add_argument('--algorithm', type=str, required=True)
    parser.add_argument('--profile', default=None, type=str)
    parser.add_argument('--save_video', action='store_true')
    args = parser.parse_args()

    # Get algorithm class and init
    algorithm = ALGOS[args.algorithm]()

    # Initialize image source
    # detects args.data, get a list of all file directory when given a directory
    # change data_source to a list of all files in the directory
    if os.path.isdir(args.data):
        data_sources = os.listdir(args.data)
    else:
        data_sources = [args.data]

    if args.cProfiler is not None:
        run(data_sources, algorithm, args.save_video)
    else:
        profile(data_sources, algorithm, args.save_video, stats=args.profile)
