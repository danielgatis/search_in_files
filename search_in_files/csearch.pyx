from io import open


def find_in_file(pattern, path, encoding, open_file=open):
    """
        Returns True when the file contains the pattern otherwise returns False
    """
    try:
        with open_file(path, encoding=encoding, errors='ignore') as f:
            for line in f:
                if line.find(pattern) > -1:
                    return True
    except:
        pass

    return False


def sort(tasks, results):
    """
        Sorts all results
    """
    matches = [tasks[i][1] for i, match in enumerate(results) if match]
    matches.sort()
    return matches
