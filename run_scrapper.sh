# Activate conda environment
eval "$(conda shell.bash hook)"
conda activate wiki_scrapper

# Function to display help
show_help() {
    echo "Usage: $0 [-p value] [-u value] [-l value]"
    echo
    echo "Parameters:"
    echo "  -p value    Input phrase for scrapping wikipedia search"
    echo "  -u value    Input proxy URL for scrapping"
    echo "  -l value    Input wikipedia links for scrapping"
}

# Initialize variables
p_value=""
u_value=""
l_value=""

# Parse options
while getopts ":p:u:l:h" opt; do
    case $opt in
        p)
            p_value="$OPTARG"
            ;;
        u)
            u_value="$OPTARG"
            ;;
        l)
            l_value="$OPTARG"
            ;;
        h)
            show_help
            exit 0
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            show_help
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            show_help
            exit 1
            ;;
    esac
done

# Check if u is an empty string
if [ -z "$u_value" ]; then
    echo "Parameter for -u is an empty string, we will not use any proxy link"
    # Check if l is an empty string
    if [ -z "$l_value"]; then
        echo "Parameter for -l is an empty string, we will not scrape wikipedia page"

        # Run scrapper for phrase search
        python main.py -p "$p_value"
    else
        # Run scrapper for phrase search and url search
        python main.py -p "$p_value" -l "$l_value"
    fi

else
    echo "Parameter for -u: $u_value, will use the proxy link"

    # Check if l is an empty string
    if [ -z "$l_value"]; then
        echo "Parameter for -l is an empty string, we will not scrape wikipedia page"

        # Run scrapper for phrase search
        python main.py -p "$p_value" -u "$u_value"
    else
        # Run scrapper for phrase search and url search
        python main.py -p "$p_value" -l "$l_value" -u "$u_value" 
    fi
fi