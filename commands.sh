



change-db(){
	if [[ -n "$1" ]]; then
		export DB_NAME="$1"
	elif [[ -n "$DB_NAME" ]]; then
		export DB_NAME="$DB_NAME"
	else
		export DB_NAME="example"
	fi

	echo -e " * Using $DB_NAME db\033]0;$DB_NAME DB\a"
	export DB_FOLDER="./$DB_NAME-db"
	export DB_PDB_FOLDER="$DB_FOLDER/pdbs"
	export DB_PROCESSED_FOLDER="$DB_FOLDER/processed"
	export DB_RESULTS_FOLDER="$DB_FOLDER/search_results"
	makedir -p $DB_PDB_FOLDER
}
change-db

build (){
	sudo docker build . -t masif-neosurf
}

run (){
	echo "$(sudo docker ps -a | grep "masif-neosurf")"
	if [[ -z "$(sudo docker ps -a | grep "masif-neosurf")" ]]; then
		echo " * Creating new Docker container..."
		sudo docker run -it -v $PWD:/home/masif-neosurf masif-neosurf
	else
		echo " * Starting up existing container..."
		sudo docker start -ia $(sudo docker ps -a |grep "masif-neosurf"|head -1|cut -d " " -f1 )
	fi
}

connect (){
	sudo docker exec -it $(sudo docker ps |grep "masif-neosurf"|head -1|rev|cut -d " " -f1 |rev) bash
}



process-list (){

	path=$(realpath $1)
	echo "Processing CODES in : $path"

	declare -a codes=()
	while read -d "," line; do
		echo $line
		process-pdb $line
	done < $path
}

process-pdb (){

	CODE=$1
	FNAME="$1.pdb"
	CHAIN="$2"
	mkdir -p $DB_PDB_FOLDER
	FILEPATH="$DB_PDB_FOLDER/$FNAME"



	if ! [[ -f "$FILEPATH" ]]; then
		curl https://files.rcsb.org/download/${CODE}.pdb -o "$FILEPATH" || return 1
	fi

	if [[ -z "$CHAIN" ]]; then
		echo "Processing ${CODE} (all chains)"
		declare -a chains=()
		while read -r line; do
			line=$(echo $line | tr -s ' ')
			#echo $line
			if [[ $(echo $line | cut -d " " -f1 ) == "ATOM" ]]; then
				chain="$(echo $line | cut -d " " -f5)"
				#echo "$line $chain"
				chain_added="0"
				#echo "${chains[@]}"

				#echo $(echo "${chains[@]}" | grep -c "$chain")
				#echo $([[ $(echo "${chains[@]}" | grep -c "$chain") -gt 0 ]])

				if [[ $(echo "${chains[@]}" | grep -c "$chain") -eq 0 ]]; then
					echo "- Detected new chain: $chain"
					chains+=("$chain")
				fi

			fi
		done < <(grep 'ATOM ' $FILEPATH | grep "CA")
	else
		echo "Processing ${CODE}_${CHAIN}"
		declare -a chains=("$CHAIN")
	fi
	for chain in ${chains[@]}; do
		echo ""
		if [[ -d $DB_PROCESSED_FOLDER/descriptors/sc05/all_feat/${CODE}_${CHAIN} ]]; then
			echo " * PDB (${CODE}_${CHAIN}) already processed"
		else
			echo " * Processing $FILEPATH ${CODE}_${chain}"
			python -W ignore ./preprocess_pdb.py $FILEPATH ${CODE}_${chain} -o $DB_PROCESSED_FOLDER
		fi

	done
}



search (){

	if [[ $# -lt 3 ]]; then
		echo "Please provide <pdb code> <chain> <num_sites>"
		return 1
	fi
	CODE=$1
	CHAIN=$2
	NUM_SITES=$3
	echo " * Filtering vertices..."
	python ./filter_vertices.py $DB_PROCESSED_FOLDER/output/all_feat_3l/pred_surfaces/$1_$2.ply $NUM_SITES
	echo ""
	echo " * Searching targets for $1_$2 in $DB_PROCESSED_FOLDER"
	VERTICE_PATH="$DB_PROCESSED_FOLDER/output/all_feat_3l/pred_surfaces/$1_$2.filtered_$3.vix"
	if [[ -f "$VERTICE_PATH" ]]; then

		echo " * Using filtered vertices from $VERTICE_PATH"
		python -W ignore masif_search.py \
		--target_dir $DB_PROCESSED_FOLDER \
		--target ${CODE}_${CHAIN} \
		--database $DB_PROCESSED_FOLDER \
		--out_dir "$DB_RESULTS_FOLDER/$NUM_SITES" \
		--site_vix_file="$VERTICE_PATH" "${@:3:}"
	else
		echo " * Filtered file: $VERTICE_PATH not found"
		echo " * Using highest scoring vertices"
		python -W ignore masif_search.py \
		--target_dir $DB_PROCESSED_FOLDER \
		--target ${CODE}_${CHAIN} \
		--database $DB_PROCESSED_FOLDER \
		--out_dir "$DB_RESULTS_FOLDER/$NUM_SITES" \
		--num_sites  $NUM_SITES "${@:3:}"
	fi
	return 1




	echo " * Results saved to $DB_RESULTS_FOLDER"
}



show (){

	echo " * Showing search results"
	python ./search_show.py "$@"
}