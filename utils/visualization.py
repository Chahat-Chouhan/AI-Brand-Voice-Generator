import matplotlib.pyplot as plt

def create_keyword_chart(top_keywords: list):
    """
    Generates a horizontal bar chart of top extracted brand keywords.
    """
    if not top_keywords:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "No Keyword Data Available", ha='center', va='center', fontsize=12)
        ax.axis('off')
        return fig

    # Extract words and counts
    words = [item[0] for item in top_keywords][::-1]
    counts = [item[1] for item in top_keywords][::-1]

    # Create figure with dark modern theme styling
    fig, ax = plt.subplots(figsize=(7, 3.5))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    bars = ax.barh(words, counts, color='#4F46E5', edgecolor='#818CF8', height=0.6)

    # Style axes and text
    ax.tick_params(colors='white', labelsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#374151')
    ax.spines['left'].set_color('#374151')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    
    plt.title("Top Vocabulary Frequency", color="white", fontsize=12, pad=10)
    plt.tight_layout()
    
    return fig
