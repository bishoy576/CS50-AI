import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, initial_page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    N = len(corpus)
    prob_of_picked_at_random = (1-damping_factor) / N
    prob_of_transition_from_initial_page = damping_factor / (len(corpus[initial_page]) if corpus[initial_page] else N)

    probability_dirtibution = {}
    for page in corpus:
        if page in corpus[initial_page]:
            probability_dirtibution[page] = prob_of_transition_from_initial_page + prob_of_picked_at_random
        else:
            probability_dirtibution[page] =  prob_of_picked_at_random
    return probability_dirtibution


    


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    possible_pages = list(corpus.keys())
    all_samples = n * [None]
    all_samples[0] = random.choice(possible_pages)
    for i in range(1, n):
        transition_prob = transition_model(corpus, all_samples[i-1], damping_factor)
        all_samples[i] = random.choices(list(transition_prob.keys()), weights=list(transition_prob.values()))[0]
    
    return {page: (all_samples.count(page) / n) for page in possible_pages}

    



def iterate_pagerank(corpus, d):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    PR = {page : 1 / N for page in corpus}
    allowed_error = 0.001
    while True:
        max_error = -float("inf")
        for p in corpus:
            prev_PR = PR[p]
            # if corpus[p]:
            PR[p] = ((1-d) / N) + d * sum([PR[i] / (len(corpus[i]) if len(corpus[i]) > 0 else N)
                                            if p in corpus[i] or not corpus[i] else 0 for i in corpus])
            # else:
            #     PR[p] = ((1-d) / N) + d * sum([PR[i] / (len(corpus[i]) if len(corpus[i]) > 0 else N) if p in corpus[i] and i != p else 0 for i in corpus])
            max_error = max(max_error, abs(prev_PR - PR[p]))
        if max_error <= allowed_error:
             return PR


            


if __name__ == "__main__":
    main()
