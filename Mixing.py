import uuid
from Container import Container
import os
import ImageProcessing
import subprocess
import math
import datetime

# mx = mixing / adr = automated dialogue replacement
from log import log


class Mixing:
    uid: str = str(uuid.uuid4())
    frame_path: str = None
    sources: tuple = None
    mx_reference: str = None
    delay_ms: int = None
    file_out_path: str = None
    successful = False


# rtd = runtime difference
def mix(mixing: Mixing, seek=(0.5, 0.85)):
    container: tuple = mixing.sources
    rtd: float = float(container[0].duration_exact) - float(container[1].duration_exact)

    log.info(f"""

{container[0].file_name} Runtime: {datetime.timedelta(seconds=container[0].duration_exact)}s FPS: {container[0].container_fps} 
{container[1].file_name} Runtime: {datetime.timedelta(seconds=container[1].duration_exact)}s FPS: {container[1].container_fps}
RTD: {rtd}s
                """)

    delay: list = []
    index_offset = None

    if not os.path.exists(mixing.frame_path):
        os.makedirs(mixing.frame_path)

    for i in range(2):
        log.info('pass {}'.format(i + 1))

        source = container[i]

        seek_time = seek[i] * container[0].duration
        vframes, time_offset = vframes_offset(source.container_fps, rtd, seek_time, index_offset)

        mx_reference = mixing.mx_reference if mixing.mx_reference else ImageProcessing.extract_frames(
            container[0].file_path, mixing.frame_path, seek_time, container[0].container_size, 1)

        adr_reference = ImageProcessing.extract_frames(container[1].file_path, mixing.frame_path, seek_time,
                                                       container[0].container_size, 1)

        adr_bulk = ImageProcessing.extract_frames(container[1].file_path, mixing.frame_path, time_offset,
                                                  container[0].container_size, vframes)

        seek_index = null_index(adr_bulk, adr_reference)

        results = {}
        for image in adr_bulk:
            results[image] = ImageProcessing.compare_image(mx_reference, image)

        result = min(results, key=lambda x: results.get(x))
        delay.append((adr_bulk.index(seek_index) - adr_bulk.index(result)))
        index_offset = adr_bulk.index(result) - adr_bulk.index(seek_index)

        log.info(
            f"Index: {adr_bulk.index(result)} Null: {adr_bulk.index(seek_index)} Difference: {results.get(result)}")

    log.info(
        [f"[Index: {delay[0]} Delay: {delay[0] / container[0].container_fps * 1000}]",
         f"[Index: {delay[1]} Delay: {delay[1] / container[1].container_fps * 1000}]"]
    )

    return calc_delay(delay, container[0].container_fps)


def merge(mixing: Mixing, delete_source=False, remove_multi_track=False):
    mx_container = mixing.sources[0]
    adr_container = mixing.sources[1]

    index = None
    for stream in adr_container.streams:
        if stream.codec_type == "audio":
            index = str(stream.index)
            break

    if index is None:
        return None

    adr_options = ""
    if remove_multi_track:
        adr_options += " -a !ger"

    try:
        p = subprocess.Popen(
            f"mkvmerge -o \"{mixing.file_out_path}\" {adr_options} \"{mx_container.file_path}\" -D -a {index} -S "
            f"--no-chapters -T -y {index}:{mixing.delay_ms} --language {index}:ger --default-track "
            f"{index}:true \"{adr_container.file_path}\" --track-order 0:0,1:{index} -q",
            stdout=subprocess.PIPE, shell=True)

        (output, err) = p.communicate()

        p_status = p.wait()
        exitcode = int(p_status)
    except Exception as ex:
        print(ex)
        exitcode = 1

    if exitcode != 0 and os.path.exists(mixing.file_out_path):
        os.remove(mixing.file_out_path)
        return False

    if delete_source and os.path.exists(mixing.file_out_path):
        os.remove(mx_container.file_path)

    return True


def load_sources(mx_source, adr_source):
    mx_container = Container(mx_source)
    adr_container = Container(adr_source)

    if not mx_container.loaded or not adr_container.loaded:
        log.error(
            'container {} loaded {}/{}'.format((mx_container.file_path, adr_container.file_path),
                                               mx_container.loaded, adr_container.loaded))
        return None

    if not int(mx_container.container_fps * 100) == int(adr_container.container_fps * 100):
        log.error('container {} fps do not match {}/{}'.format((mx_container.file_path, adr_container.file_path),
                                                               mx_container.container_fps, adr_container.container_fps))
        return None

    return mx_container, adr_container


def vframes_offset(fps: float, rtd: float, seek_time: float, offset=None):
    vframes = None
    time_offset = None

    if type(offset) is int or (type(offset) is str and offset.isnumeric()):
        data = calc_run_two(offset, seek_time, fps)
        vframes = data['vframes']
        time_offset = data['time_offset']
    else:
        vframes = calc_run_one_vframes(rtd, fps)
        time_offset = seek_time - int(vframes / 2 / fps)

    return vframes, time_offset


def null_index(bulk, bulk_reference):
    if ImageProcessing.same_image(bulk[0], bulk[1]):
        del bulk[0]
    for i in bulk:
        if ImageProcessing.same_image(i, bulk_reference):
            return i
    return None


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


def calc_run_two(index_offset, seek_time, fps):
    if abs(index_offset) <= 10:
        time_offset = seek_time - round(50 / fps)
        vframes = 100
    else:
        if index_offset < 0:
            time_offset = seek_time - round(abs(index_offset) / fps) - 1
            vframes = abs(index_offset) + math.ceil(fps) * 2
        elif index_offset > 0:
            time_offset = seek_time
            vframes = index_offset + math.ceil(fps)

        if vframes < 100:
            vframes = 100

    return {"time_offset": time_offset, "vframes": vframes}


def calc_delay(delay, fps):
    # if -2 <= (delay[0] - delay[1]) <= 2:
    cdelay = [delay[0] / fps * 1000, delay[1] / fps * 1000]
    cdelay.sort(reverse=True)
    return int((cdelay[0] + cdelay[1]) / 2), -2 <= (delay[0] - delay[1]) <= 2
