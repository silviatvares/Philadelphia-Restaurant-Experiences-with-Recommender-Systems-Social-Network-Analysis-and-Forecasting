import traceback
import pandas as pd
import numpy as np
import os


def read_data_in_chunks(file, cols=None, chunk_size=500000, nr_chunks=-1, criteria=None):
    """
    Reads large JSON files in chunks to avoid memory overload. Allows filtering columns
    and applying criteria for filtering rows.

    Parameters:
    file (str): Path to the JSON file.
    cols (list): List of columns to be extracted from each chunk. If None, all columns are read.
    chunk_size (int): Number of rows per chunk.
    nr_chunks (int): Number of chunks to read. If -1, reads until the file ends.
    criteria (function): A function to filter rows in the DataFrame.

    Returns:
    pd.DataFrame: A concatenated DataFrame from all chunks.
    """

    print(f'Reading JSON file in chunks from {file}...')

    try:
        # Initialize the JSON reader
        reader = pd.read_json(path_or_buf=file, chunksize=chunk_size, lines=True)
    except ValueError as e:
        print(f'Error! Failed to read file {file}. Reason: {e}')
        return None

    chunk_list = []
    chunks_read = 0

    while nr_chunks != 0:
        try:
            # Read next chunk
            chunk = next(reader)
            chunks_read += 1

            # Extract specific columns if provided
            if cols is not None:
                chunk = chunk[cols]

            # Apply criteria to filter rows
            if criteria is not None:
                chunk = criteria(chunk)

            chunk_list.append(chunk)
            print(f'Chunk {chunks_read} read: Shape {chunk.shape}')

        except StopIteration:
            print('Info: No more chunks to read.')
            break
        except Exception as e:
            print(f'Error while processing chunk {chunks_read}: {e}')
            print(traceback.format_exc())
            break

        nr_chunks -= 1

    if chunk_list:
        try:
            # Concatenate all chunks into a single DataFrame
            result_df = pd.concat(chunk_list, ignore_index=True, join='outer', axis=0)
            print(f'Concatenation complete. Final DataFrame shape: {result_df.shape}')
            return result_df
        except Exception as e:
            print(f'Error while concatenating chunks: {e}')
            print(traceback.format_exc())
            return None
    else:
        print('Warning: No chunks were processed.')
        return None
    

def find_project_root(search_file=".git"):
    current_dir = os.getcwd()
    
    while current_dir != os.path.dirname(current_dir):  # Stop at the root directory
        if search_file in os.listdir(current_dir):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    
    return None  # Return None if the root is not found
    

def get_popular_recommendations(trainset, top_n=10):
    item_counts = dict()

    # Iterate through the trainset to count item ratings
    for _, item_id, rating in trainset.all_ratings():
        if item_id in item_counts:
            item_counts[item_id][1] = (item_counts[item_id][1] * item_counts[item_id][0] + rating) / (item_counts[item_id][0] + 1)
            item_counts[item_id][0] += 1
        
        else:
            # All values are in the format [count, average of rating]
            item_counts[item_id] = [1]
            item_counts[item_id].append(rating)

    # Sort items by higher ratings with weigth 2 and number of ratings with weight 1
    popular_items = sorted(item_counts.items(), key=lambda x: 2 * x[1][1] + 1 * x[1][0], reverse=True)

    # Get the top N most popular items (e.g., top 10)
    top_n = popular_items[:top_n]
    return [trainset.to_raw_iid(i) for i, _ in top_n]


# Recommend top N items for a user using a recommender model
def recommend_top_n(algo, trainset, user_id, n=10):
    user_ratings = trainset.ur[user_id]
    items = [item_id for (item_id, _) in user_ratings]
    
    item_scores = {}
    # this is actually not the most correct way to do this, but it works
    for item_id in trainset.all_items():
        if item_id not in items:
            prediction = algo.predict(trainset.to_raw_uid(user_id), trainset.to_raw_iid(item_id), verbose=True)
            item_scores[item_id] = prediction.est
    
    top_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)[:n]

    #from raw_id to actual_id
    return [(trainset.to_raw_iid(i), r) for i, r in top_items]


def precision_at_k(recommendations: list[str], ground_truth: list[str]) -> float:
    hits = len(set(recommendations).intersection(set(ground_truth)))
    return round(hits / len(recommendations), 3)


def recall_at_k(recommendations: list[str], ground_truth: list[str]) -> float:
    hits = len(set(recommendations).intersection(set(ground_truth)))
    return round(hits / len(ground_truth), 3)


def f1_at_k(recommendations: list[str], ground_truth: list[str]) -> float:
    precision = precision_at_k(recommendations, ground_truth)
    recall = recall_at_k(recommendations, ground_truth)
    if (precision + recall) == 0:
        print("Precision and Recall are zero!")
        return None
    return round(2 * precision * recall / (precision + recall), 3)


def average_precision(recommendations, ground_truth):
    """
    Computes the Average Precision at rank k (AP@k).
    
    Parameters:
    predicted_list (list): The ordered list of recommended items.
    ground_truth (list): The list of relevant items.
    k (int): The maximum rank position to consider.

    Returns:
    float: AP@k score.
    """
    
    relevant_items = 0
    precision_sum = 0.0
    
    for i, item in enumerate(recommendations):
        if item in ground_truth:
            relevant_items += 1
            precision_at_i = relevant_items / (i + 1)
            precision_sum += precision_at_i
    
    # If no relevant items were found in the top-k, return 0
    if relevant_items == 0:
        return 0.0
    
    # Return average precision
    return round(precision_sum / relevant_items, 3)



def dcg_at_k(recommendations, ground_truth):
    """
    Computes the Discounted Cumulative Gain (DCG) at rank k.
    
    Parameters:
    recommendations (list): The ordered list of recommended items.
    ground_truth (list): The list of relevant items.
    k (int): The maximum rank position to consider for DCG.

    Returns:
    float: DCG score at rank k.
    """
    
    dcg = 0.0
    
    for i, item in enumerate(recommendations):
        if item in ground_truth:  # Relevance is binary (1 if relevant, 0 otherwise)
            rel_i = 1  # Assign a relevance score of 1 if the item is in the ground truth
        else:
            rel_i = 0
        
        # i+1 because enumerate starts at 0, we need positions starting at 1
        dcg += rel_i / np.log2((i + 1) + 1)
    
    return round(dcg, 3)