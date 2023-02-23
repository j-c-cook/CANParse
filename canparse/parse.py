import pathlib
from typing import Tuple, List

# Non-python library requirements
import can  # pip install python-can
import cantools  # pip install cantools
from cantools.typechecking import DecodeResultType


def dissect_rollover_name(file_name) -> Tuple:
    path = pathlib.Path(file_name)
    stem_split = path.stem.split('_')
    bus_name = stem_split[0]
    date = stem_split[1][:10]
    return bus_name, date


def filter_file_names(all_file_names, names, dates) -> List[str]:
    def _filter(_name, _category) -> bool:
        if r':' in _category:
            _keep = True
        elif _name in _category:
            _keep = True
        else:
            _keep = False
        return _keep

    file_names = []
    for _, file_name in enumerate(all_file_names):
        bus_name, date = dissect_rollover_name(file_name)

        # Check to see if the file passes the filter
        keep_name = _filter(bus_name, names)
        keep_date = _filter(date, dates)

        if keep_name and keep_date:
            file_names.append(file_name)

    return file_names


def sort_object_list_by_instance(objects: list, instance: str) -> List:
    """
    Sort a list of objects by an instance.

    :author: Jack C. Cook

    Parameters
    ----------
    objects : list
              A list of user-defined types, i.e. objects.
    instance : str
               The name of the instance to be sorted.
    Returns
    -------
    _sorted : list
              The list of objects sorted by key.
    """
    # Create a dictionary of the unsorted instances
    unsorted_idx: dict = \
        {i: getattr(objects[i], instance) for i, m in enumerate(objects)}
    # Sort the dictionary by value (creates a list of tuples)
    sorted_idx: list = sorted(unsorted_idx.items(), key=lambda x: x[1])

    return [objects[idx] for idx, _ in sorted_idx]


def decode_message(can_msg: can.Message, dbs: List[cantools.db.Database], allow_truncated=True):
    for _, db in enumerate(dbs):
        try:
            db_msg = db.get_message_by_frame_id(can_msg.arbitration_id)
        except KeyError:
            continue
        try:
            msg_decoded: DecodeResultType = db_msg.decode(
                can_msg.data, allow_truncated=allow_truncated)
        except cantools.db.errors.DecodeError:
            continue
        return msg_decoded, db_msg

    # print('Unable to decode the message.', file=stderr)
    return None, None
