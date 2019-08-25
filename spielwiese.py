import math

import FileHandler
import ImageProcessing


def calc_run_one_vframes(difference, fps):
    frame_diff = int(abs(difference) * fps * 2)
    if frame_diff <= 150:
        if frame_diff + 60 > 150:
            return frame_diff + 60
        return 150
    elif frame_diff > 10000:
        return 150
    else:
        return frame_diff + 60


def calc_delay(delay, fps):
    if -2 <= (delay[0] - delay[1]) <= 2:
        cdelay = [delay[0] / fps * 1000, delay[1] / fps * 1000]
        cdelay.sort(reverse=True)
        return int((cdelay[0] + cdelay[1]) / 2)

    message = f"the provided delay values {delay} are not similar enough"
    print(message)
    return None


def null_index(bulk, bulk_reference):
    if ImageProcessing.same_image(bulk[0], bulk[1]):
        del bulk[0]
    for i in bulk:
        if ImageProcessing.same_image(i, bulk_reference):
            return i
    return None


def sync():
    sources = [["C:/Users/ch30393/Documents/video/test-1.jpg", "C:/Users/ch30393/Documents/video/test-2.jpg"],
               "C:/Users/ch30393/Documents/video/output2.mp4"]
    seek_time = (27, 450)
    fps = 24.0

    time1 = 591.894000
    time2 = 593.288000
    rtd = time1 - time2
    vframes = calc_run_one_vframes(rtd, fps)

    delay = []

    frame_output = "C:/Users/ch30393/Documents/cli_sync/frames"

    for run in range(2):
        print(f"running {run + 1} lap")

        time_offset = seek_time[run] - int(vframes / 2 / fps)

        reference = sources[0][run]

        bulk_reference = \
            FileHandler.load_frames(
                ImageProcessing.extract_frames(sources[1], frame_output,
                                               seek_time[run],
                                               "720x480",
                                               1), frame_output)[0]
        bulk = FileHandler.load_frames(
            ImageProcessing.extract_frames(sources[1], frame_output,
                                           time_offset,
                                           "720x480",
                                           vframes), frame_output)

        seek_index = null_index(bulk, bulk_reference)

        results = {}
        for image in bulk:
            results[image] = ImageProcessing.compare_image(reference, image)

        result = min(results, key=lambda x: results.get(x))
        delay.append((bulk.index(seek_index) - bulk.index(result)))
        print(f"Index: {bulk.index(result)} Null: {bulk.index(seek_index)} Difference: {results.get(result)}")

    message = [f"[Index: {delay[0]} Delay: {delay[0] / fps * 1000}]",
               f"[Index: {delay[1]} Delay: {delay[1] / fps * 1000}]"]
    print(message[0])
    print(message[1])

    delay_ms = calc_delay(delay, fps)
    if delay_ms is not None:
        delay_ms = delay_ms
        print(delay_ms)


sync()
