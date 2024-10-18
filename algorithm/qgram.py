import numpy as np


def getProfiles(string, q=2):
    """Calculate profiles of the given string. 

    Every `q` consecutive characters constitute a profile. This function
    returns a `dict` instance whose keys are the profiles and whose values 
    are the corresponding frequency in the string.

    Example: abcab, q=2 -> `{'ab': 2, 'bc': 1, 'ca': 1}`
    """
    profiles = dict()
    for i in range(0, len(string) - q + 1):
        substr = string[i:i+q]
        if substr in profiles:
            profiles[substr] += 1
        else:
            profiles[substr] = 1

    return profiles

def getVectors(*strings, q=2):
    """Calculate vectors of the given strings for distance comparing. 

    The parameters can be several strings or several profile `dict`'s. 
    """
    # Calculate profiles if necessary
    if isinstance(strings[0], str):
        profiles = [getProfiles(string, q) for string in strings]
    else:
        profiles = strings

    # Get the union of all profiles
    all_profiles = set().union(*(set(profile.keys()) for profile in profiles))
    all_profiles = sorted(all_profiles)

    # Turn profiles into vectors
    vectors = [list() for _ in strings]
    for vector, existing_profiles in zip(vectors, profiles):
        for profile in all_profiles:
            if profile in existing_profiles:
                vector.append(existing_profiles[profile])
            else:
                vector.append(0)

    return all_profiles, vectors

def cosineDistance(vec1, vec2):
    """
    Calculate cosine distance of two vectors: 1 - (a.b)/(|a||b|)
    """
    a = np.array(vec1)
    b = np.array(vec2)
    return 1 - np.sqrt(np.dot(a, b) ** 2 / (np.dot(a, a) * np.dot(b, b)))


def qgramDistance(str1, str2, q=2):
    """
    Calculate qgram distance of two strings.

    Qgram distance is the sum of the absolute distances of each dimension of
    the string vectors (L1 Norm).
    """
    _, (a, b) = getVectors(str1, str2, q=q)
    return np.linalg.norm(np.array(a) - np.array(b), 1)

def cosQgramDistance(str1, str2, q=2):
    """
    Calculate qgram-cosine distance of two strings.

    Qgram-cosine distance is the cosine distance of two string vectors.
    """
    _, (a, b) = getVectors(str1, str2, q=q)
    return cosineDistance(a, b)


if __name__ == "__main__":
    strings = ["Jun  9 06:06:51 combo anacron: anacron startup succeeded",
               "Jun  9 06:06:51 combo atd: atd startup succeeded",
               "Jun  9 06:06:51 combo readahead: Starting background readahead:",
               "Jun  9 06:06:51 combo rc: Starting readahead:  succeeded",
               "Jun  9 06:06:52 combo messagebus: messagebus startup succeeded"]
    
    d = "Jun  9 06:07:06 combo httpd: httpd startup succeeded"

    for i in strings:
        print(cosQgramDistance(d,i))