PGDMP          
        
    |            bdinnovacion    16.3    16.3 �               0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false                       0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false                       0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false                       1262    67962    bdinnovacion    DATABASE     �   CREATE DATABASE bdinnovacion WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Spanish_Colombia.1252';
    DROP DATABASE bdinnovacion;
                postgres    false                        3079    67963    pgcrypto 	   EXTENSION     <   CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
    DROP EXTENSION pgcrypto;
                   false                       0    0    EXTENSION pgcrypto    COMMENT     <   COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';
                        false    2            0           1255    68000    borrar_registro_mas_viejo()    FUNCTION       CREATE FUNCTION public.borrar_registro_mas_viejo() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Verificar si el número de registros es mayor o igual a 10000
    IF (SELECT COUNT(*) FROM public.tbl_msgerror) >= 10000 THEN
        -- Borrar el registro más viejo basado en la fecha_error
        DELETE FROM public.tbl_msgerror
        WHERE id = (
            SELECT id FROM public.tbl_msgerror
            ORDER BY fecha_error ASC
            LIMIT 1
        );
    END IF;
    RETURN NEW;
END;
$$;
 2   DROP FUNCTION public.borrar_registro_mas_viejo();
       public          postgres    false            1           1255    68001 $   delete_json_entity(text, text, text) 	   PROCEDURE     =  CREATE PROCEDURE public.delete_json_entity(IN p_table_name text, IN where_condition text, INOUT mensaje text DEFAULT NULL::text)
    LANGUAGE plpgsql
    AS $$
DECLARE
    affected_rows int;
BEGIN
    -- Ejecutar la eliminación
    EXECUTE format('DELETE FROM %I WHERE %s',
                    p_table_name, where_condition);
    
    GET DIAGNOSTICS affected_rows = ROW_COUNT;

    IF affected_rows > 0 THEN
        mensaje := format('Se eliminaron %s filas correctamente.', affected_rows);
    ELSE
        mensaje := 'No se encontraron filas para eliminar.';
    END IF;
EXCEPTION
    WHEN others THEN
        mensaje := SQLERRM;
        -- Registrar el error en la tabla tbl_msgerror
        INSERT INTO tbl_msgerror (mensaje_error, numero_error, fecha_error)
        VALUES (mensaje, SQLSTATE, CURRENT_TIMESTAMP);
END;
$$;
 m   DROP PROCEDURE public.delete_json_entity(IN p_table_name text, IN where_condition text, INOUT mensaje text);
       public          postgres    false            =           1255    68002 %   insert_json_entity(text, jsonb, text) 	   PROCEDURE     �  CREATE PROCEDURE public.insert_json_entity(IN p_table_name text, IN json_data jsonb, INOUT mensaje text DEFAULT NULL::text)
    LANGUAGE plpgsql
    AS $$
DECLARE
    column_names text;
    column_values text;
    table_columns text[];
    pk_column text;
    pk_is_serial boolean;
BEGIN
    -- Obtener el nombre de la columna de clave primaria
    SELECT a.attname INTO pk_column
    FROM   pg_index i
    JOIN   pg_attribute a ON a.attrelid = i.indrelid
                         AND a.attnum = ANY(i.indkey)
    WHERE  i.indrelid = p_table_name::regclass
    AND    i.indisprimary;

    -- Verificar si la clave primaria es serial (autonumérica)
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = p_table_name
        AND column_name = pk_column
        AND column_default LIKE 'nextval%'
    ) INTO pk_is_serial;

    -- Obtener todas las columnas de la tabla
    SELECT array_agg(column_name::text)
    INTO table_columns
    FROM information_schema.columns
    WHERE table_name = p_table_name;

    -- Construir los nombres de columnas y valores desde el JSON
    SELECT string_agg(quote_ident(key), ', '),
           string_agg(quote_nullable(value::text), ', ')
    INTO column_names, column_values
    FROM jsonb_each_text(json_data)
    WHERE (pk_is_serial AND key != pk_column) OR (NOT pk_is_serial AND key = ANY(table_columns));
    
    BEGIN
        -- Ejecutar la inserción
        EXECUTE format('INSERT INTO %I (%s) VALUES (%s)',
                        p_table_name, column_names, column_values);
        mensaje := 'Inserción realizada correctamente.';
    EXCEPTION
        WHEN unique_violation THEN
            mensaje := SQLERRM;
            PERFORM log_error(mensaje, SQLSTATE);
        WHEN foreign_key_violation THEN
            mensaje := SQLERRM;
            PERFORM log_error(mensaje, SQLSTATE);
        WHEN OTHERS THEN
            mensaje := SQLERRM;
            PERFORM log_error(mensaje, SQLSTATE);
    END;
END;
$$;
 h   DROP PROCEDURE public.insert_json_entity(IN p_table_name text, IN json_data jsonb, INOUT mensaje text);
       public          postgres    false            >           1255    68003    log_error(text, text)    FUNCTION     �   CREATE FUNCTION public.log_error(mensaje_error text, numero_error text) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO tbl_msgerror (mensaje_error, numero_error)
    VALUES (mensaje_error, numero_error);
END;
$$;
 G   DROP FUNCTION public.log_error(mensaje_error text, numero_error text);
       public          postgres    false            ?           1255    68004 =   select_json_entity(text, text, text, text, text, jsonb, text) 	   PROCEDURE     `  CREATE PROCEDURE public.select_json_entity(IN p_table_name text, OUT result jsonb, INOUT mensaje text, IN where_condition text DEFAULT NULL::text, IN order_by text DEFAULT NULL::text, IN limit_clause text DEFAULT NULL::text, IN json_params jsonb DEFAULT '{}'::jsonb, IN select_columns text DEFAULT '*'::text)
    LANGUAGE plpgsql
    AS $$
DECLARE
    query text;
    param_name text;
    param_value text;
BEGIN
    -- Construir la consulta
    query := format('SELECT jsonb_agg(to_jsonb(t)) FROM (SELECT %s FROM %s', select_columns, p_table_name);
    
    IF where_condition IS NOT NULL AND where_condition != '' THEN
        query := query || ' WHERE ' || where_condition;
    END IF;
    
    IF order_by IS NOT NULL AND order_by != '' THEN
        query := query || ' ORDER BY ' || order_by;
    END IF;
    
    IF limit_clause IS NOT NULL AND limit_clause != '' THEN
        query := query || ' LIMIT ' || limit_clause;
    END IF;
    
    query := query || ') t';

    -- Reemplazar los marcadores de posición con valores del json_params
    FOR param_name, param_value IN SELECT * FROM jsonb_each_text(json_params)
    LOOP
        query := replace(query, ':' || param_name, quote_literal(param_value));
    END LOOP;

    -- Ejecutar la consulta
    BEGIN
        EXECUTE query INTO result;
        IF result IS NULL THEN
            result := '[]'::jsonb;
            mensaje := 'No se encontraron resultados.';
        ELSE
            mensaje := 'Consulta ejecutada correctamente.';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            mensaje := SQLERRM;
            result := NULL;
    END;
END;
$$;
 �   DROP PROCEDURE public.select_json_entity(IN p_table_name text, OUT result jsonb, INOUT mensaje text, IN where_condition text, IN order_by text, IN limit_clause text, IN json_params jsonb, IN select_columns text);
       public          postgres    false            @           1255    68005 +   update_json_entity(text, jsonb, text, text) 	   PROCEDURE     
  CREATE PROCEDURE public.update_json_entity(IN p_table_name text, IN json_data jsonb, IN where_condition text, INOUT mensaje text DEFAULT NULL::text)
    LANGUAGE plpgsql
    AS $$
DECLARE
    update_columns text;
    affected_rows int;
BEGIN
    -- Construir la cadena de actualización
    SELECT string_agg(quote_ident(key) || ' = ' || quote_nullable(value::text), ', ')
    INTO update_columns
    FROM jsonb_each_text(json_data);
    
    -- Ejecutar la actualización
    EXECUTE format('UPDATE %I SET %s WHERE %s',
                    p_table_name, update_columns, where_condition);
    
    GET DIAGNOSTICS affected_rows = ROW_COUNT;

    IF affected_rows > 0 THEN
        mensaje := format('Se actualizaron %s filas correctamente.', affected_rows);
    ELSE
        mensaje := 'No se encontraron filas para actualizar.';
    END IF;
EXCEPTION
    WHEN others THEN
        mensaje := SQLERRM;
        -- Opcionalmente, puedes registrar el error en una tabla de errores
        -- PERFORM log_error(mensaje, SQLSTATE);
END;
$$;
 �   DROP PROCEDURE public.update_json_entity(IN p_table_name text, IN json_data jsonb, IN where_condition text, INOUT mensaje text);
       public          postgres    false            �            1259    68006 
   aplicacion    TABLE     �   CREATE TABLE public.aplicacion (
    id integer NOT NULL,
    titulo character varying(200) NOT NULL,
    sigla character varying(50) NOT NULL
);
    DROP TABLE public.aplicacion;
       public         heap    postgres    false            �            1259    68009    aplicacion_id_seq    SEQUENCE     �   CREATE SEQUENCE public.aplicacion_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.aplicacion_id_seq;
       public          postgres    false    216                       0    0    aplicacion_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.aplicacion_id_seq OWNED BY public.aplicacion.id;
          public          postgres    false    217            �            1259    68010    area_i    TABLE     k   CREATE TABLE public.area_i (
    id_area_i integer NOT NULL,
    nombre character varying(200) NOT NULL
);
    DROP TABLE public.area_i;
       public         heap    postgres    false            �            1259    68013    area_i_id_area_i_seq    SEQUENCE     �   CREATE SEQUENCE public.area_i_id_area_i_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.area_i_id_area_i_seq;
       public          postgres    false    218                       0    0    area_i_id_area_i_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.area_i_id_area_i_seq OWNED BY public.area_i.id_area_i;
          public          postgres    false    219            �            1259    68014 	   area_idea    TABLE     �   CREATE TABLE public.area_idea (
    id_area_idea integer NOT NULL,
    codigo_idea integer NOT NULL,
    id_area_i integer NOT NULL
);
    DROP TABLE public.area_idea;
       public         heap    postgres    false            �            1259    68017    area_idea_id_area_idea_seq    SEQUENCE     �   CREATE SEQUENCE public.area_idea_id_area_idea_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 1   DROP SEQUENCE public.area_idea_id_area_idea_seq;
       public          postgres    false    220            	           0    0    area_idea_id_area_idea_seq    SEQUENCE OWNED BY     Y   ALTER SEQUENCE public.area_idea_id_area_idea_seq OWNED BY public.area_idea.id_area_idea;
          public          postgres    false    221            �            1259    68018    area_o    TABLE     k   CREATE TABLE public.area_o (
    id_area_o integer NOT NULL,
    nombre character varying(100) NOT NULL
);
    DROP TABLE public.area_o;
       public         heap    postgres    false            �            1259    68021    area_o_id_area_o_seq    SEQUENCE     �   CREATE SEQUENCE public.area_o_id_area_o_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.area_o_id_area_o_seq;
       public          postgres    false    222            
           0    0    area_o_id_area_o_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.area_o_id_area_o_seq OWNED BY public.area_o.id_area_o;
          public          postgres    false    223            �            1259    68022    area_oportunidad    TABLE     �   CREATE TABLE public.area_oportunidad (
    id_area_oportunidad integer NOT NULL,
    codigo_oportunidad integer NOT NULL,
    id_area_o integer NOT NULL
);
 $   DROP TABLE public.area_oportunidad;
       public         heap    postgres    false            �            1259    68025 (   area_oportunidad_id_area_oportunidad_seq    SEQUENCE     �   CREATE SEQUENCE public.area_oportunidad_id_area_oportunidad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ?   DROP SEQUENCE public.area_oportunidad_id_area_oportunidad_seq;
       public          postgres    false    224                       0    0 (   area_oportunidad_id_area_oportunidad_seq    SEQUENCE OWNED BY     u   ALTER SEQUENCE public.area_oportunidad_id_area_oportunidad_seq OWNED BY public.area_oportunidad.id_area_oportunidad;
          public          postgres    false    225            �            1259    68026    areas_expertise    TABLE     �   CREATE TABLE public.areas_expertise (
    id integer NOT NULL,
    usuario_email character varying(255) NOT NULL,
    area character varying(100)
);
 #   DROP TABLE public.areas_expertise;
       public         heap    postgres    false            �            1259    68029    areas_expertise_id_seq    SEQUENCE     �   CREATE SEQUENCE public.areas_expertise_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 -   DROP SEQUENCE public.areas_expertise_id_seq;
       public          postgres    false    226                       0    0    areas_expertise_id_seq    SEQUENCE OWNED BY     Q   ALTER SEQUENCE public.areas_expertise_id_seq OWNED BY public.areas_expertise.id;
          public          postgres    false    227            �            1259    68075    estado_i    TABLE     m   CREATE TABLE public.estado_i (
    id_estado_i integer NOT NULL,
    tipo character varying(200) NOT NULL
);
    DROP TABLE public.estado_i;
       public         heap    postgres    false            �            1259    68078    estado_i_id_estado_i_seq    SEQUENCE     �   CREATE SEQUENCE public.estado_i_id_estado_i_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.estado_i_id_estado_i_seq;
       public          postgres    false    228                       0    0    estado_i_id_estado_i_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.estado_i_id_estado_i_seq OWNED BY public.estado_i.id_estado_i;
          public          postgres    false    229            �            1259    68079    estado_idea    TABLE     �   CREATE TABLE public.estado_idea (
    id_estado_idea integer NOT NULL,
    id_estado_i integer NOT NULL,
    codigo_idea integer NOT NULL
);
    DROP TABLE public.estado_idea;
       public         heap    postgres    false            �            1259    68082    estado_idea_id_estado_idea_seq    SEQUENCE     �   CREATE SEQUENCE public.estado_idea_id_estado_idea_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public.estado_idea_id_estado_idea_seq;
       public          postgres    false    230                       0    0    estado_idea_id_estado_idea_seq    SEQUENCE OWNED BY     a   ALTER SEQUENCE public.estado_idea_id_estado_idea_seq OWNED BY public.estado_idea.id_estado_idea;
          public          postgres    false    231            �            1259    68083    estado_o    TABLE     m   CREATE TABLE public.estado_o (
    id_estado_o integer NOT NULL,
    tipo character varying(100) NOT NULL
);
    DROP TABLE public.estado_o;
       public         heap    postgres    false            �            1259    68086    estado_o_id_estado_o_seq    SEQUENCE     �   CREATE SEQUENCE public.estado_o_id_estado_o_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.estado_o_id_estado_o_seq;
       public          postgres    false    232                       0    0    estado_o_id_estado_o_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.estado_o_id_estado_o_seq OWNED BY public.estado_o.id_estado_o;
          public          postgres    false    233            �            1259    68087    estado_oportunidad    TABLE     �   CREATE TABLE public.estado_oportunidad (
    id_estado_oportunidad integer NOT NULL,
    id_estado_o integer NOT NULL,
    codigo_oportunidad integer NOT NULL
);
 &   DROP TABLE public.estado_oportunidad;
       public         heap    postgres    false            �            1259    68090 ,   estado_oportunidad_id_estado_oportunidad_seq    SEQUENCE     �   CREATE SEQUENCE public.estado_oportunidad_id_estado_oportunidad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 C   DROP SEQUENCE public.estado_oportunidad_id_estado_oportunidad_seq;
       public          postgres    false    234                       0    0 ,   estado_oportunidad_id_estado_oportunidad_seq    SEQUENCE OWNED BY     }   ALTER SEQUENCE public.estado_oportunidad_id_estado_oportunidad_seq OWNED BY public.estado_oportunidad.id_estado_oportunidad;
          public          postgres    false    235            �            1259    68091    foco_innovacion    TABLE     {   CREATE TABLE public.foco_innovacion (
    id_foco_innovacion integer NOT NULL,
    name character varying(100) NOT NULL
);
 #   DROP TABLE public.foco_innovacion;
       public         heap    postgres    false            �            1259    68094 &   foco_innovacion_id_foco_innovacion_seq    SEQUENCE     �   CREATE SEQUENCE public.foco_innovacion_id_foco_innovacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 =   DROP SEQUENCE public.foco_innovacion_id_foco_innovacion_seq;
       public          postgres    false    236                       0    0 &   foco_innovacion_id_foco_innovacion_seq    SEQUENCE OWNED BY     q   ALTER SEQUENCE public.foco_innovacion_id_foco_innovacion_seq OWNED BY public.foco_innovacion.id_foco_innovacion;
          public          postgres    false    237            �            1259    68095    idea    TABLE     �  CREATE TABLE public.idea (
    codigo_idea integer NOT NULL,
    id_tipo_innovacion integer NOT NULL,
    id_foco_innovacion integer NOT NULL,
    titulo character varying(50) NOT NULL,
    descripcion character varying(250) NOT NULL,
    fecha_creacion date NOT NULL,
    palabras_claves character varying(250) NOT NULL,
    recursos_requeridos integer NOT NULL,
    archivo_multimedia character varying(200) NOT NULL,
    creador_por character varying(255) NOT NULL,
    estado boolean DEFAULT false
);
    DROP TABLE public.idea;
       public         heap    postgres    false            �            1259    68100    idea_codigo_idea_seq    SEQUENCE     �   CREATE SEQUENCE public.idea_codigo_idea_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.idea_codigo_idea_seq;
       public          postgres    false    238                       0    0    idea_codigo_idea_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.idea_codigo_idea_seq OWNED BY public.idea.codigo_idea;
          public          postgres    false    239            �            1259    68101    idea_usuario    TABLE     �   CREATE TABLE public.idea_usuario (
    id_idea_usuario integer NOT NULL,
    email_usuario character varying(100) NOT NULL,
    codigo_idea integer NOT NULL
);
     DROP TABLE public.idea_usuario;
       public         heap    postgres    false            �            1259    68104     idea_usuario_id_idea_usuario_seq    SEQUENCE     �   CREATE SEQUENCE public.idea_usuario_id_idea_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 7   DROP SEQUENCE public.idea_usuario_id_idea_usuario_seq;
       public          postgres    false    240                       0    0     idea_usuario_id_idea_usuario_seq    SEQUENCE OWNED BY     e   ALTER SEQUENCE public.idea_usuario_id_idea_usuario_seq OWNED BY public.idea_usuario.id_idea_usuario;
          public          postgres    false    241            �            1259    68105    informacion_adicional    TABLE     �   CREATE TABLE public.informacion_adicional (
    id integer NOT NULL,
    usuario_email character varying(255) NOT NULL,
    info text
);
 )   DROP TABLE public.informacion_adicional;
       public         heap    postgres    false            �            1259    68110    informacion_adicional_id_seq    SEQUENCE     �   CREATE SEQUENCE public.informacion_adicional_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.informacion_adicional_id_seq;
       public          postgres    false    242                       0    0    informacion_adicional_id_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public.informacion_adicional_id_seq OWNED BY public.informacion_adicional.id;
          public          postgres    false    243            �            1259    68121    login_perfil    TABLE       CREATE TABLE public.login_perfil (
    id bigint NOT NULL,
    nombre character varying(100),
    rol character varying(50) NOT NULL,
    fecha_nacimiento date,
    direccion character varying(200),
    descripcion text,
    usuario_id character varying(254) NOT NULL
);
     DROP TABLE public.login_perfil;
       public         heap    postgres    false            �            1259    68126    login_perfil_id_seq    SEQUENCE     �   ALTER TABLE public.login_perfil ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.login_perfil_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    244                       1259    71567    notificaciones    TABLE       CREATE TABLE public.notificaciones (
    id integer NOT NULL,
    usuario_email character varying(255) NOT NULL,
    tipo_entidad character varying(50) NOT NULL,
    entidad_titulo character varying(255) NOT NULL,
    mensaje_default text NOT NULL,
    mensaje_experto text,
    experto_email character varying(255) NOT NULL,
    fecha_creacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    fecha_leida timestamp without time zone,
    leida boolean DEFAULT false,
    accion character varying(50) NOT NULL
);
 "   DROP TABLE public.notificaciones;
       public         heap    postgres    false                       1259    71566    notificaciones_id_seq    SEQUENCE     �   CREATE SEQUENCE public.notificaciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public.notificaciones_id_seq;
       public          postgres    false    263                       0    0    notificaciones_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public.notificaciones_id_seq OWNED BY public.notificaciones.id;
          public          postgres    false    262            �            1259    68127    oportunidad    TABLE     �  CREATE TABLE public.oportunidad (
    codigo_oportunidad integer NOT NULL,
    titulo character varying(200) NOT NULL,
    descripcion character varying(250) NOT NULL,
    fecha_creacion date NOT NULL,
    palabras_claves character varying(200) NOT NULL,
    archivo_multimedia character varying(200) NOT NULL,
    creador_por character varying(50),
    id_foco_innovacion integer,
    id_tipo_innovacion integer,
    recursos_requeridos integer,
    estado boolean DEFAULT false
);
    DROP TABLE public.oportunidad;
       public         heap    postgres    false            �            1259    68132 "   oportunidad_codigo_oportunidad_seq    SEQUENCE     �   CREATE SEQUENCE public.oportunidad_codigo_oportunidad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 9   DROP SEQUENCE public.oportunidad_codigo_oportunidad_seq;
       public          postgres    false    246                       0    0 "   oportunidad_codigo_oportunidad_seq    SEQUENCE OWNED BY     i   ALTER SEQUENCE public.oportunidad_codigo_oportunidad_seq OWNED BY public.oportunidad.codigo_oportunidad;
          public          postgres    false    247            �            1259    68133    oportunidad_usuario    TABLE     �   CREATE TABLE public.oportunidad_usuario (
    id_oportunidad_usuario integer NOT NULL,
    email_usuario character varying(100) NOT NULL,
    codigo_oportunidad integer NOT NULL
);
 '   DROP TABLE public.oportunidad_usuario;
       public         heap    postgres    false            �            1259    68136 .   oportunidad_usuario_id_oportunidad_usuario_seq    SEQUENCE     �   CREATE SEQUENCE public.oportunidad_usuario_id_oportunidad_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 E   DROP SEQUENCE public.oportunidad_usuario_id_oportunidad_usuario_seq;
       public          postgres    false    248                       0    0 .   oportunidad_usuario_id_oportunidad_usuario_seq    SEQUENCE OWNED BY     �   ALTER SEQUENCE public.oportunidad_usuario_id_oportunidad_usuario_seq OWNED BY public.oportunidad_usuario.id_oportunidad_usuario;
          public          postgres    false    249            �            1259    68137    perfil    TABLE     �   CREATE TABLE public.perfil (
    id integer NOT NULL,
    usuario_email character varying(255) NOT NULL,
    nombre character varying(100),
    rol character varying(50),
    fecha_nacimiento date,
    direccion text,
    descripcion text
);
    DROP TABLE public.perfil;
       public         heap    postgres    false            �            1259    68147    perfil_id_seq    SEQUENCE     �   CREATE SEQUENCE public.perfil_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public.perfil_id_seq;
       public          postgres    false    250                       0    0    perfil_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE public.perfil_id_seq OWNED BY public.perfil.id;
          public          postgres    false    251                       1259    71600    proyecto    TABLE     �  CREATE TABLE public.proyecto (
    id_proyecto integer NOT NULL,
    tipo_origen character varying(50) NOT NULL,
    id_origen integer NOT NULL,
    titulo character varying(255) NOT NULL,
    descripcion text,
    fecha_creacion timestamp without time zone NOT NULL,
    palabras_claves text,
    recursos_requeridos integer,
    archivo_multimedia text,
    creador_por character varying(255) NOT NULL,
    id_tipo_innovacion integer,
    id_foco_innovacion integer,
    estado boolean DEFAULT true,
    fecha_aprobacion timestamp without time zone,
    aprobado_por character varying(255),
    observaciones text,
    desarrollador_por text,
    area_unidad_desarrollo text
);
    DROP TABLE public.proyecto;
       public         heap    postgres    false            
           1259    71599    proyecto_id_proyecto_seq    SEQUENCE     �   CREATE SEQUENCE public.proyecto_id_proyecto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.proyecto_id_proyecto_seq;
       public          postgres    false    267                       0    0    proyecto_id_proyecto_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.proyecto_id_proyecto_seq OWNED BY public.proyecto.id_proyecto;
          public          postgres    false    266            �            1259    68160    rol    TABLE     `   CREATE TABLE public.rol (
    id integer NOT NULL,
    nombre character varying(50) NOT NULL
);
    DROP TABLE public.rol;
       public         heap    postgres    false            �            1259    68163 
   rol_id_seq    SEQUENCE     �   CREATE SEQUENCE public.rol_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 !   DROP SEQUENCE public.rol_id_seq;
       public          postgres    false    252                       0    0 
   rol_id_seq    SEQUENCE OWNED BY     9   ALTER SEQUENCE public.rol_id_seq OWNED BY public.rol.id;
          public          postgres    false    253            	           1259    71581    solucion    TABLE       CREATE TABLE public.solucion (
    codigo_solucion integer NOT NULL,
    id_tipo_innovacion integer NOT NULL,
    id_foco_innovacion integer NOT NULL,
    titulo character varying(255) NOT NULL,
    descripcion text NOT NULL,
    fecha_creacion timestamp without time zone NOT NULL,
    palabras_claves text,
    recursos_requeridos integer,
    archivo_multimedia text,
    creador_por character varying(255) NOT NULL,
    desarrollador_por text,
    area_unidad_desarrollo text,
    estado boolean DEFAULT false
);
    DROP TABLE public.solucion;
       public         heap    postgres    false                       1259    71580    solucion_codigo_solucion_seq    SEQUENCE     �   CREATE SEQUENCE public.solucion_codigo_solucion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 3   DROP SEQUENCE public.solucion_codigo_solucion_seq;
       public          postgres    false    265                       0    0    solucion_codigo_solucion_seq    SEQUENCE OWNED BY     ]   ALTER SEQUENCE public.solucion_codigo_solucion_seq OWNED BY public.solucion.codigo_solucion;
          public          postgres    false    264            �            1259    68168    tbl_msgerror_id_seq    SEQUENCE     �   CREATE SEQUENCE public.tbl_msgerror_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.tbl_msgerror_id_seq;
       public          postgres    false            �            1259    68169    tbl_msgerror    TABLE     �   CREATE TABLE public.tbl_msgerror (
    id integer DEFAULT nextval('public.tbl_msgerror_id_seq'::regclass) NOT NULL,
    mensaje_error text,
    numero_error text,
    fecha_error timestamp with time zone DEFAULT now()
);
     DROP TABLE public.tbl_msgerror;
       public         heap    postgres    false    254                        1259    68176    tipo_innovacion    TABLE     {   CREATE TABLE public.tipo_innovacion (
    id_tipo_innovacion integer NOT NULL,
    name character varying(100) NOT NULL
);
 #   DROP TABLE public.tipo_innovacion;
       public         heap    postgres    false                       1259    68179 &   tipo_innovacion_id_tipo_innovacion_seq    SEQUENCE     �   CREATE SEQUENCE public.tipo_innovacion_id_tipo_innovacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 =   DROP SEQUENCE public.tipo_innovacion_id_tipo_innovacion_seq;
       public          postgres    false    256                       0    0 &   tipo_innovacion_id_tipo_innovacion_seq    SEQUENCE OWNED BY     q   ALTER SEQUENCE public.tipo_innovacion_id_tipo_innovacion_seq OWNED BY public.tipo_innovacion.id_tipo_innovacion;
          public          postgres    false    257                       1259    68180    tipo_oportunidad    TABLE     }   CREATE TABLE public.tipo_oportunidad (
    id_tipo_oportunidad integer NOT NULL,
    name character varying(200) NOT NULL
);
 $   DROP TABLE public.tipo_oportunidad;
       public         heap    postgres    false                       1259    68183 (   tipo_oportunidad_id_tipo_oportunidad_seq    SEQUENCE     �   CREATE SEQUENCE public.tipo_oportunidad_id_tipo_oportunidad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ?   DROP SEQUENCE public.tipo_oportunidad_id_tipo_oportunidad_seq;
       public          postgres    false    258                       0    0 (   tipo_oportunidad_id_tipo_oportunidad_seq    SEQUENCE OWNED BY     u   ALTER SEQUENCE public.tipo_oportunidad_id_tipo_oportunidad_seq OWNED BY public.tipo_oportunidad.id_tipo_oportunidad;
          public          postgres    false    259                       1259    68184    usuario    TABLE       CREATE TABLE public.usuario (
    email character varying(100) NOT NULL,
    password character varying(200) NOT NULL,
    is_active boolean NOT NULL,
    is_staff boolean NOT NULL,
    is_superuser boolean NOT NULL,
    last_login timestamp with time zone
);
    DROP TABLE public.usuario;
       public         heap    postgres    false                       1259    68195    usuariorolaplicacion    TABLE     �   CREATE TABLE public.usuariorolaplicacion (
    fkemail character varying(100) NOT NULL,
    fkidrol integer NOT NULL,
    fkidaplicacion integer NOT NULL,
    fechaasignacion timestamp with time zone DEFAULT now() NOT NULL
);
 (   DROP TABLE public.usuariorolaplicacion;
       public         heap    postgres    false            �           2604    68199    aplicacion id    DEFAULT     n   ALTER TABLE ONLY public.aplicacion ALTER COLUMN id SET DEFAULT nextval('public.aplicacion_id_seq'::regclass);
 <   ALTER TABLE public.aplicacion ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    217    216            �           2604    68200    area_i id_area_i    DEFAULT     t   ALTER TABLE ONLY public.area_i ALTER COLUMN id_area_i SET DEFAULT nextval('public.area_i_id_area_i_seq'::regclass);
 ?   ALTER TABLE public.area_i ALTER COLUMN id_area_i DROP DEFAULT;
       public          postgres    false    219    218            �           2604    68201    area_idea id_area_idea    DEFAULT     �   ALTER TABLE ONLY public.area_idea ALTER COLUMN id_area_idea SET DEFAULT nextval('public.area_idea_id_area_idea_seq'::regclass);
 E   ALTER TABLE public.area_idea ALTER COLUMN id_area_idea DROP DEFAULT;
       public          postgres    false    221    220            �           2604    68202    area_o id_area_o    DEFAULT     t   ALTER TABLE ONLY public.area_o ALTER COLUMN id_area_o SET DEFAULT nextval('public.area_o_id_area_o_seq'::regclass);
 ?   ALTER TABLE public.area_o ALTER COLUMN id_area_o DROP DEFAULT;
       public          postgres    false    223    222            �           2604    68203 $   area_oportunidad id_area_oportunidad    DEFAULT     �   ALTER TABLE ONLY public.area_oportunidad ALTER COLUMN id_area_oportunidad SET DEFAULT nextval('public.area_oportunidad_id_area_oportunidad_seq'::regclass);
 S   ALTER TABLE public.area_oportunidad ALTER COLUMN id_area_oportunidad DROP DEFAULT;
       public          postgres    false    225    224            �           2604    68204    areas_expertise id    DEFAULT     x   ALTER TABLE ONLY public.areas_expertise ALTER COLUMN id SET DEFAULT nextval('public.areas_expertise_id_seq'::regclass);
 A   ALTER TABLE public.areas_expertise ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    227    226            �           2604    68205    estado_i id_estado_i    DEFAULT     |   ALTER TABLE ONLY public.estado_i ALTER COLUMN id_estado_i SET DEFAULT nextval('public.estado_i_id_estado_i_seq'::regclass);
 C   ALTER TABLE public.estado_i ALTER COLUMN id_estado_i DROP DEFAULT;
       public          postgres    false    229    228            �           2604    68206    estado_idea id_estado_idea    DEFAULT     �   ALTER TABLE ONLY public.estado_idea ALTER COLUMN id_estado_idea SET DEFAULT nextval('public.estado_idea_id_estado_idea_seq'::regclass);
 I   ALTER TABLE public.estado_idea ALTER COLUMN id_estado_idea DROP DEFAULT;
       public          postgres    false    231    230            �           2604    68207    estado_o id_estado_o    DEFAULT     |   ALTER TABLE ONLY public.estado_o ALTER COLUMN id_estado_o SET DEFAULT nextval('public.estado_o_id_estado_o_seq'::regclass);
 C   ALTER TABLE public.estado_o ALTER COLUMN id_estado_o DROP DEFAULT;
       public          postgres    false    233    232            �           2604    68208 (   estado_oportunidad id_estado_oportunidad    DEFAULT     �   ALTER TABLE ONLY public.estado_oportunidad ALTER COLUMN id_estado_oportunidad SET DEFAULT nextval('public.estado_oportunidad_id_estado_oportunidad_seq'::regclass);
 W   ALTER TABLE public.estado_oportunidad ALTER COLUMN id_estado_oportunidad DROP DEFAULT;
       public          postgres    false    235    234            �           2604    68209 "   foco_innovacion id_foco_innovacion    DEFAULT     �   ALTER TABLE ONLY public.foco_innovacion ALTER COLUMN id_foco_innovacion SET DEFAULT nextval('public.foco_innovacion_id_foco_innovacion_seq'::regclass);
 Q   ALTER TABLE public.foco_innovacion ALTER COLUMN id_foco_innovacion DROP DEFAULT;
       public          postgres    false    237    236            �           2604    68210    idea codigo_idea    DEFAULT     t   ALTER TABLE ONLY public.idea ALTER COLUMN codigo_idea SET DEFAULT nextval('public.idea_codigo_idea_seq'::regclass);
 ?   ALTER TABLE public.idea ALTER COLUMN codigo_idea DROP DEFAULT;
       public          postgres    false    239    238            �           2604    68211    idea_usuario id_idea_usuario    DEFAULT     �   ALTER TABLE ONLY public.idea_usuario ALTER COLUMN id_idea_usuario SET DEFAULT nextval('public.idea_usuario_id_idea_usuario_seq'::regclass);
 K   ALTER TABLE public.idea_usuario ALTER COLUMN id_idea_usuario DROP DEFAULT;
       public          postgres    false    241    240            �           2604    68212    informacion_adicional id    DEFAULT     �   ALTER TABLE ONLY public.informacion_adicional ALTER COLUMN id SET DEFAULT nextval('public.informacion_adicional_id_seq'::regclass);
 G   ALTER TABLE public.informacion_adicional ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    243    242            �           2604    71570    notificaciones id    DEFAULT     v   ALTER TABLE ONLY public.notificaciones ALTER COLUMN id SET DEFAULT nextval('public.notificaciones_id_seq'::regclass);
 @   ALTER TABLE public.notificaciones ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    263    262    263            �           2604    68213    oportunidad codigo_oportunidad    DEFAULT     �   ALTER TABLE ONLY public.oportunidad ALTER COLUMN codigo_oportunidad SET DEFAULT nextval('public.oportunidad_codigo_oportunidad_seq'::regclass);
 M   ALTER TABLE public.oportunidad ALTER COLUMN codigo_oportunidad DROP DEFAULT;
       public          postgres    false    247    246            �           2604    68214 *   oportunidad_usuario id_oportunidad_usuario    DEFAULT     �   ALTER TABLE ONLY public.oportunidad_usuario ALTER COLUMN id_oportunidad_usuario SET DEFAULT nextval('public.oportunidad_usuario_id_oportunidad_usuario_seq'::regclass);
 Y   ALTER TABLE public.oportunidad_usuario ALTER COLUMN id_oportunidad_usuario DROP DEFAULT;
       public          postgres    false    249    248            �           2604    68215 	   perfil id    DEFAULT     f   ALTER TABLE ONLY public.perfil ALTER COLUMN id SET DEFAULT nextval('public.perfil_id_seq'::regclass);
 8   ALTER TABLE public.perfil ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    251    250            �           2604    71603    proyecto id_proyecto    DEFAULT     |   ALTER TABLE ONLY public.proyecto ALTER COLUMN id_proyecto SET DEFAULT nextval('public.proyecto_id_proyecto_seq'::regclass);
 C   ALTER TABLE public.proyecto ALTER COLUMN id_proyecto DROP DEFAULT;
       public          postgres    false    266    267    267            �           2604    68216    rol id    DEFAULT     `   ALTER TABLE ONLY public.rol ALTER COLUMN id SET DEFAULT nextval('public.rol_id_seq'::regclass);
 5   ALTER TABLE public.rol ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    253    252            �           2604    71584    solucion codigo_solucion    DEFAULT     �   ALTER TABLE ONLY public.solucion ALTER COLUMN codigo_solucion SET DEFAULT nextval('public.solucion_codigo_solucion_seq'::regclass);
 G   ALTER TABLE public.solucion ALTER COLUMN codigo_solucion DROP DEFAULT;
       public          postgres    false    264    265    265            �           2604    68218 "   tipo_innovacion id_tipo_innovacion    DEFAULT     �   ALTER TABLE ONLY public.tipo_innovacion ALTER COLUMN id_tipo_innovacion SET DEFAULT nextval('public.tipo_innovacion_id_tipo_innovacion_seq'::regclass);
 Q   ALTER TABLE public.tipo_innovacion ALTER COLUMN id_tipo_innovacion DROP DEFAULT;
       public          postgres    false    257    256            �           2604    68219 $   tipo_oportunidad id_tipo_oportunidad    DEFAULT     �   ALTER TABLE ONLY public.tipo_oportunidad ALTER COLUMN id_tipo_oportunidad SET DEFAULT nextval('public.tipo_oportunidad_id_tipo_oportunidad_seq'::regclass);
 S   ALTER TABLE public.tipo_oportunidad ALTER COLUMN id_tipo_oportunidad DROP DEFAULT;
       public          postgres    false    259    258            �          0    68006 
   aplicacion 
   TABLE DATA           7   COPY public.aplicacion (id, titulo, sigla) FROM stdin;
    public          postgres    false    216   �2      �          0    68010    area_i 
   TABLE DATA           3   COPY public.area_i (id_area_i, nombre) FROM stdin;
    public          postgres    false    218   o3      �          0    68014 	   area_idea 
   TABLE DATA           I   COPY public.area_idea (id_area_idea, codigo_idea, id_area_i) FROM stdin;
    public          postgres    false    220   �3      �          0    68018    area_o 
   TABLE DATA           3   COPY public.area_o (id_area_o, nombre) FROM stdin;
    public          postgres    false    222   �3      �          0    68022    area_oportunidad 
   TABLE DATA           ^   COPY public.area_oportunidad (id_area_oportunidad, codigo_oportunidad, id_area_o) FROM stdin;
    public          postgres    false    224   �3      �          0    68026    areas_expertise 
   TABLE DATA           B   COPY public.areas_expertise (id, usuario_email, area) FROM stdin;
    public          postgres    false    226   �3      �          0    68075    estado_i 
   TABLE DATA           5   COPY public.estado_i (id_estado_i, tipo) FROM stdin;
    public          postgres    false    228   �4      �          0    68079    estado_idea 
   TABLE DATA           O   COPY public.estado_idea (id_estado_idea, id_estado_i, codigo_idea) FROM stdin;
    public          postgres    false    230   �4      �          0    68083    estado_o 
   TABLE DATA           5   COPY public.estado_o (id_estado_o, tipo) FROM stdin;
    public          postgres    false    232   5      �          0    68087    estado_oportunidad 
   TABLE DATA           d   COPY public.estado_oportunidad (id_estado_oportunidad, id_estado_o, codigo_oportunidad) FROM stdin;
    public          postgres    false    234   /5      �          0    68091    foco_innovacion 
   TABLE DATA           C   COPY public.foco_innovacion (id_foco_innovacion, name) FROM stdin;
    public          postgres    false    236   L5      �          0    68095    idea 
   TABLE DATA           �   COPY public.idea (codigo_idea, id_tipo_innovacion, id_foco_innovacion, titulo, descripcion, fecha_creacion, palabras_claves, recursos_requeridos, archivo_multimedia, creador_por, estado) FROM stdin;
    public          postgres    false    238   �5      �          0    68101    idea_usuario 
   TABLE DATA           S   COPY public.idea_usuario (id_idea_usuario, email_usuario, codigo_idea) FROM stdin;
    public          postgres    false    240   �7      �          0    68105    informacion_adicional 
   TABLE DATA           H   COPY public.informacion_adicional (id, usuario_email, info) FROM stdin;
    public          postgres    false    242   8      �          0    68121    login_perfil 
   TABLE DATA           m   COPY public.login_perfil (id, nombre, rol, fecha_nacimiento, direccion, descripcion, usuario_id) FROM stdin;
    public          postgres    false    244   I9      �          0    71567    notificaciones 
   TABLE DATA           �   COPY public.notificaciones (id, usuario_email, tipo_entidad, entidad_titulo, mensaje_default, mensaje_experto, experto_email, fecha_creacion, fecha_leida, leida, accion) FROM stdin;
    public          postgres    false    263   �9      �          0    68127    oportunidad 
   TABLE DATA           �   COPY public.oportunidad (codigo_oportunidad, titulo, descripcion, fecha_creacion, palabras_claves, archivo_multimedia, creador_por, id_foco_innovacion, id_tipo_innovacion, recursos_requeridos, estado) FROM stdin;
    public          postgres    false    246   =;      �          0    68133    oportunidad_usuario 
   TABLE DATA           h   COPY public.oportunidad_usuario (id_oportunidad_usuario, email_usuario, codigo_oportunidad) FROM stdin;
    public          postgres    false    248   �<      �          0    68137    perfil 
   TABLE DATA           j   COPY public.perfil (id, usuario_email, nombre, rol, fecha_nacimiento, direccion, descripcion) FROM stdin;
    public          postgres    false    250   
=      �          0    71600    proyecto 
   TABLE DATA           =  COPY public.proyecto (id_proyecto, tipo_origen, id_origen, titulo, descripcion, fecha_creacion, palabras_claves, recursos_requeridos, archivo_multimedia, creador_por, id_tipo_innovacion, id_foco_innovacion, estado, fecha_aprobacion, aprobado_por, observaciones, desarrollador_por, area_unidad_desarrollo) FROM stdin;
    public          postgres    false    267   �>      �          0    68160    rol 
   TABLE DATA           )   COPY public.rol (id, nombre) FROM stdin;
    public          postgres    false    252   �@      �          0    71581    solucion 
   TABLE DATA           �   COPY public.solucion (codigo_solucion, id_tipo_innovacion, id_foco_innovacion, titulo, descripcion, fecha_creacion, palabras_claves, recursos_requeridos, archivo_multimedia, creador_por, desarrollador_por, area_unidad_desarrollo, estado) FROM stdin;
    public          postgres    false    265   �@      �          0    68169    tbl_msgerror 
   TABLE DATA           T   COPY public.tbl_msgerror (id, mensaje_error, numero_error, fecha_error) FROM stdin;
    public          postgres    false    255   �A      �          0    68176    tipo_innovacion 
   TABLE DATA           C   COPY public.tipo_innovacion (id_tipo_innovacion, name) FROM stdin;
    public          postgres    false    256   :E      �          0    68180    tipo_oportunidad 
   TABLE DATA           E   COPY public.tipo_oportunidad (id_tipo_oportunidad, name) FROM stdin;
    public          postgres    false    258   E      �          0    68184    usuario 
   TABLE DATA           a   COPY public.usuario (email, password, is_active, is_staff, is_superuser, last_login) FROM stdin;
    public          postgres    false    260   �E      �          0    68195    usuariorolaplicacion 
   TABLE DATA           a   COPY public.usuariorolaplicacion (fkemail, fkidrol, fkidaplicacion, fechaasignacion) FROM stdin;
    public          postgres    false    261   ]L                 0    0    aplicacion_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.aplicacion_id_seq', 4, true);
          public          postgres    false    217                       0    0    area_i_id_area_i_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.area_i_id_area_i_seq', 1, false);
          public          postgres    false    219                        0    0    area_idea_id_area_idea_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.area_idea_id_area_idea_seq', 1, false);
          public          postgres    false    221            !           0    0    area_o_id_area_o_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.area_o_id_area_o_seq', 1, false);
          public          postgres    false    223            "           0    0 (   area_oportunidad_id_area_oportunidad_seq    SEQUENCE SET     W   SELECT pg_catalog.setval('public.area_oportunidad_id_area_oportunidad_seq', 1, false);
          public          postgres    false    225            #           0    0    areas_expertise_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.areas_expertise_id_seq', 17, true);
          public          postgres    false    227            $           0    0    estado_i_id_estado_i_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.estado_i_id_estado_i_seq', 1, false);
          public          postgres    false    229            %           0    0    estado_idea_id_estado_idea_seq    SEQUENCE SET     M   SELECT pg_catalog.setval('public.estado_idea_id_estado_idea_seq', 1, false);
          public          postgres    false    231            &           0    0    estado_o_id_estado_o_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.estado_o_id_estado_o_seq', 1, false);
          public          postgres    false    233            '           0    0 ,   estado_oportunidad_id_estado_oportunidad_seq    SEQUENCE SET     [   SELECT pg_catalog.setval('public.estado_oportunidad_id_estado_oportunidad_seq', 1, false);
          public          postgres    false    235            (           0    0 &   foco_innovacion_id_foco_innovacion_seq    SEQUENCE SET     T   SELECT pg_catalog.setval('public.foco_innovacion_id_foco_innovacion_seq', 8, true);
          public          postgres    false    237            )           0    0    idea_codigo_idea_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.idea_codigo_idea_seq', 43, true);
          public          postgres    false    239            *           0    0     idea_usuario_id_idea_usuario_seq    SEQUENCE SET     O   SELECT pg_catalog.setval('public.idea_usuario_id_idea_usuario_seq', 1, false);
          public          postgres    false    241            +           0    0    informacion_adicional_id_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.informacion_adicional_id_seq', 17, true);
          public          postgres    false    243            ,           0    0    login_perfil_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.login_perfil_id_seq', 5, true);
          public          postgres    false    245            -           0    0    notificaciones_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.notificaciones_id_seq', 63, true);
          public          postgres    false    262            .           0    0 "   oportunidad_codigo_oportunidad_seq    SEQUENCE SET     Q   SELECT pg_catalog.setval('public.oportunidad_codigo_oportunidad_seq', 19, true);
          public          postgres    false    247            /           0    0 .   oportunidad_usuario_id_oportunidad_usuario_seq    SEQUENCE SET     ]   SELECT pg_catalog.setval('public.oportunidad_usuario_id_oportunidad_usuario_seq', 1, false);
          public          postgres    false    249            0           0    0    perfil_id_seq    SEQUENCE SET     <   SELECT pg_catalog.setval('public.perfil_id_seq', 18, true);
          public          postgres    false    251            1           0    0    proyecto_id_proyecto_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.proyecto_id_proyecto_seq', 8, true);
          public          postgres    false    266            2           0    0 
   rol_id_seq    SEQUENCE SET     8   SELECT pg_catalog.setval('public.rol_id_seq', 3, true);
          public          postgres    false    253            3           0    0    solucion_codigo_solucion_seq    SEQUENCE SET     K   SELECT pg_catalog.setval('public.solucion_codigo_solucion_seq', 18, true);
          public          postgres    false    264            4           0    0    tbl_msgerror_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.tbl_msgerror_id_seq', 37, true);
          public          postgres    false    254            5           0    0 &   tipo_innovacion_id_tipo_innovacion_seq    SEQUENCE SET     T   SELECT pg_catalog.setval('public.tipo_innovacion_id_tipo_innovacion_seq', 4, true);
          public          postgres    false    257            6           0    0 (   tipo_oportunidad_id_tipo_oportunidad_seq    SEQUENCE SET     W   SELECT pg_catalog.setval('public.tipo_oportunidad_id_tipo_oportunidad_seq', 1, false);
          public          postgres    false    259            �           2606    68221    aplicacion aplicacion_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.aplicacion
    ADD CONSTRAINT aplicacion_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.aplicacion DROP CONSTRAINT aplicacion_pkey;
       public            postgres    false    216            �           2606    68223    area_i area_i_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY public.area_i
    ADD CONSTRAINT area_i_pkey PRIMARY KEY (id_area_i);
 <   ALTER TABLE ONLY public.area_i DROP CONSTRAINT area_i_pkey;
       public            postgres    false    218            �           2606    68225    area_idea area_idea_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public.area_idea
    ADD CONSTRAINT area_idea_pkey PRIMARY KEY (id_area_idea);
 B   ALTER TABLE ONLY public.area_idea DROP CONSTRAINT area_idea_pkey;
       public            postgres    false    220            �           2606    68227    area_o area_o_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY public.area_o
    ADD CONSTRAINT area_o_pkey PRIMARY KEY (id_area_o);
 <   ALTER TABLE ONLY public.area_o DROP CONSTRAINT area_o_pkey;
       public            postgres    false    222            �           2606    68229 &   area_oportunidad area_oportunidad_pkey 
   CONSTRAINT     u   ALTER TABLE ONLY public.area_oportunidad
    ADD CONSTRAINT area_oportunidad_pkey PRIMARY KEY (id_area_oportunidad);
 P   ALTER TABLE ONLY public.area_oportunidad DROP CONSTRAINT area_oportunidad_pkey;
       public            postgres    false    224            �           2606    68231 $   areas_expertise areas_expertise_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.areas_expertise
    ADD CONSTRAINT areas_expertise_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.areas_expertise DROP CONSTRAINT areas_expertise_pkey;
       public            postgres    false    226            �           2606    68261    estado_i estado_i_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.estado_i
    ADD CONSTRAINT estado_i_pkey PRIMARY KEY (id_estado_i);
 @   ALTER TABLE ONLY public.estado_i DROP CONSTRAINT estado_i_pkey;
       public            postgres    false    228            �           2606    68263    estado_idea estado_idea_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.estado_idea
    ADD CONSTRAINT estado_idea_pkey PRIMARY KEY (id_estado_idea);
 F   ALTER TABLE ONLY public.estado_idea DROP CONSTRAINT estado_idea_pkey;
       public            postgres    false    230            �           2606    68265    estado_o estado_o_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.estado_o
    ADD CONSTRAINT estado_o_pkey PRIMARY KEY (id_estado_o);
 @   ALTER TABLE ONLY public.estado_o DROP CONSTRAINT estado_o_pkey;
       public            postgres    false    232            �           2606    68267 *   estado_oportunidad estado_oportunidad_pkey 
   CONSTRAINT     {   ALTER TABLE ONLY public.estado_oportunidad
    ADD CONSTRAINT estado_oportunidad_pkey PRIMARY KEY (id_estado_oportunidad);
 T   ALTER TABLE ONLY public.estado_oportunidad DROP CONSTRAINT estado_oportunidad_pkey;
       public            postgres    false    234            �           2606    68269 $   foco_innovacion foco_innovacion_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.foco_innovacion
    ADD CONSTRAINT foco_innovacion_pkey PRIMARY KEY (id_foco_innovacion);
 N   ALTER TABLE ONLY public.foco_innovacion DROP CONSTRAINT foco_innovacion_pkey;
       public            postgres    false    236            �           2606    68271    idea idea_pkey 
   CONSTRAINT     U   ALTER TABLE ONLY public.idea
    ADD CONSTRAINT idea_pkey PRIMARY KEY (codigo_idea);
 8   ALTER TABLE ONLY public.idea DROP CONSTRAINT idea_pkey;
       public            postgres    false    238            �           2606    68273    idea_usuario idea_usuario_pkey 
   CONSTRAINT     i   ALTER TABLE ONLY public.idea_usuario
    ADD CONSTRAINT idea_usuario_pkey PRIMARY KEY (id_idea_usuario);
 H   ALTER TABLE ONLY public.idea_usuario DROP CONSTRAINT idea_usuario_pkey;
       public            postgres    false    240                        2606    68275 0   informacion_adicional informacion_adicional_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.informacion_adicional
    ADD CONSTRAINT informacion_adicional_pkey PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.informacion_adicional DROP CONSTRAINT informacion_adicional_pkey;
       public            postgres    false    242                       2606    68281    login_perfil login_perfil_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.login_perfil
    ADD CONSTRAINT login_perfil_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY public.login_perfil DROP CONSTRAINT login_perfil_pkey;
       public            postgres    false    244                       2606    68283 (   login_perfil login_perfil_usuario_id_key 
   CONSTRAINT     i   ALTER TABLE ONLY public.login_perfil
    ADD CONSTRAINT login_perfil_usuario_id_key UNIQUE (usuario_id);
 R   ALTER TABLE ONLY public.login_perfil DROP CONSTRAINT login_perfil_usuario_id_key;
       public            postgres    false    244                       2606    71576 "   notificaciones notificaciones_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_pkey PRIMARY KEY (id);
 L   ALTER TABLE ONLY public.notificaciones DROP CONSTRAINT notificaciones_pkey;
       public            postgres    false    263                       2606    68285    oportunidad oportunidad_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.oportunidad
    ADD CONSTRAINT oportunidad_pkey PRIMARY KEY (codigo_oportunidad);
 F   ALTER TABLE ONLY public.oportunidad DROP CONSTRAINT oportunidad_pkey;
       public            postgres    false    246            	           2606    68287 ,   oportunidad_usuario oportunidad_usuario_pkey 
   CONSTRAINT     ~   ALTER TABLE ONLY public.oportunidad_usuario
    ADD CONSTRAINT oportunidad_usuario_pkey PRIMARY KEY (id_oportunidad_usuario);
 V   ALTER TABLE ONLY public.oportunidad_usuario DROP CONSTRAINT oportunidad_usuario_pkey;
       public            postgres    false    248                       2606    68297    perfil perfil_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.perfil
    ADD CONSTRAINT perfil_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.perfil DROP CONSTRAINT perfil_pkey;
       public            postgres    false    250                       2606    68299    perfil perfil_usuario_email_key 
   CONSTRAINT     c   ALTER TABLE ONLY public.perfil
    ADD CONSTRAINT perfil_usuario_email_key UNIQUE (usuario_email);
 I   ALTER TABLE ONLY public.perfil DROP CONSTRAINT perfil_usuario_email_key;
       public            postgres    false    250            "           2606    71608    proyecto proyecto_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.proyecto
    ADD CONSTRAINT proyecto_pkey PRIMARY KEY (id_proyecto);
 @   ALTER TABLE ONLY public.proyecto DROP CONSTRAINT proyecto_pkey;
       public            postgres    false    267                       2606    68301    rol rol_pkey 
   CONSTRAINT     J   ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (id);
 6   ALTER TABLE ONLY public.rol DROP CONSTRAINT rol_pkey;
       public            postgres    false    252                        2606    71588    solucion solucion_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY public.solucion
    ADD CONSTRAINT solucion_pkey PRIMARY KEY (codigo_solucion);
 @   ALTER TABLE ONLY public.solucion DROP CONSTRAINT solucion_pkey;
       public            postgres    false    265                       2606    68305    tbl_msgerror tbl_msgerror_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.tbl_msgerror
    ADD CONSTRAINT tbl_msgerror_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY public.tbl_msgerror DROP CONSTRAINT tbl_msgerror_pkey;
       public            postgres    false    255                       2606    68307 $   tipo_innovacion tipo_innovacion_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.tipo_innovacion
    ADD CONSTRAINT tipo_innovacion_pkey PRIMARY KEY (id_tipo_innovacion);
 N   ALTER TABLE ONLY public.tipo_innovacion DROP CONSTRAINT tipo_innovacion_pkey;
       public            postgres    false    256                       2606    68309 &   tipo_oportunidad tipo_oportunidad_pkey 
   CONSTRAINT     u   ALTER TABLE ONLY public.tipo_oportunidad
    ADD CONSTRAINT tipo_oportunidad_pkey PRIMARY KEY (id_tipo_oportunidad);
 P   ALTER TABLE ONLY public.tipo_oportunidad DROP CONSTRAINT tipo_oportunidad_pkey;
       public            postgres    false    258                       2606    68315    usuario usuario_pkey 
   CONSTRAINT     U   ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (email);
 >   ALTER TABLE ONLY public.usuario DROP CONSTRAINT usuario_pkey;
       public            postgres    false    260                       2606    68321 .   usuariorolaplicacion usuariorolaplicacion_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY public.usuariorolaplicacion
    ADD CONSTRAINT usuariorolaplicacion_pkey PRIMARY KEY (fkemail, fkidrol, fkidaplicacion);
 X   ALTER TABLE ONLY public.usuariorolaplicacion DROP CONSTRAINT usuariorolaplicacion_pkey;
       public            postgres    false    261    261    261                       1259    71579 
   idx_accion    INDEX     G   CREATE INDEX idx_accion ON public.notificaciones USING btree (accion);
    DROP INDEX public.idx_accion;
       public            postgres    false    263                       1259    71578    idx_entidad_titulo    INDEX     W   CREATE INDEX idx_entidad_titulo ON public.notificaciones USING btree (entidad_titulo);
 &   DROP INDEX public.idx_entidad_titulo;
       public            postgres    false    263                       1259    71577    idx_usuario_email    INDEX     U   CREATE INDEX idx_usuario_email ON public.notificaciones USING btree (usuario_email);
 %   DROP INDEX public.idx_usuario_email;
       public            postgres    false    263                       1259    68336 %   login_perfil_usuario_id_8cfa6ed3_like    INDEX     x   CREATE INDEX login_perfil_usuario_id_8cfa6ed3_like ON public.login_perfil USING btree (usuario_id varchar_pattern_ops);
 9   DROP INDEX public.login_perfil_usuario_id_8cfa6ed3_like;
       public            postgres    false    244            <           2620    68346 .   tbl_msgerror trigger_borrar_registro_mas_viejo    TRIGGER     �   CREATE TRIGGER trigger_borrar_registro_mas_viejo AFTER INSERT ON public.tbl_msgerror FOR EACH ROW EXECUTE FUNCTION public.borrar_registro_mas_viejo();
 G   DROP TRIGGER trigger_borrar_registro_mas_viejo ON public.tbl_msgerror;
       public          postgres    false    255    304            #           2606    68347 "   area_idea area_idea_id_area_i_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.area_idea
    ADD CONSTRAINT area_idea_id_area_i_fkey FOREIGN KEY (id_area_i) REFERENCES public.area_i(id_area_i) ON UPDATE CASCADE ON DELETE CASCADE;
 L   ALTER TABLE ONLY public.area_idea DROP CONSTRAINT area_idea_id_area_i_fkey;
       public          postgres    false    4840    220    218            $           2606    68352 0   area_oportunidad area_oportunidad_id_area_o_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.area_oportunidad
    ADD CONSTRAINT area_oportunidad_id_area_o_fkey FOREIGN KEY (id_area_o) REFERENCES public.area_o(id_area_o) ON UPDATE CASCADE ON DELETE CASCADE;
 Z   ALTER TABLE ONLY public.area_oportunidad DROP CONSTRAINT area_oportunidad_id_area_o_fkey;
       public          postgres    false    222    4844    224            %           2606    68357 2   areas_expertise areas_expertise_usuario_email_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.areas_expertise
    ADD CONSTRAINT areas_expertise_usuario_email_fkey FOREIGN KEY (usuario_email) REFERENCES public.usuario(email) ON DELETE CASCADE;
 \   ALTER TABLE ONLY public.areas_expertise DROP CONSTRAINT areas_expertise_usuario_email_fkey;
       public          postgres    false    4887    226    260            5           2606    68382 !   usuariorolaplicacion cons_fkemail    FK CONSTRAINT     �   ALTER TABLE ONLY public.usuariorolaplicacion
    ADD CONSTRAINT cons_fkemail FOREIGN KEY (fkemail) REFERENCES public.usuario(email);
 K   ALTER TABLE ONLY public.usuariorolaplicacion DROP CONSTRAINT cons_fkemail;
       public          postgres    false    260    4887    261            6           2606    68387 (   usuariorolaplicacion cons_fkidaplicacion    FK CONSTRAINT     �   ALTER TABLE ONLY public.usuariorolaplicacion
    ADD CONSTRAINT cons_fkidaplicacion FOREIGN KEY (fkidaplicacion) REFERENCES public.aplicacion(id);
 R   ALTER TABLE ONLY public.usuariorolaplicacion DROP CONSTRAINT cons_fkidaplicacion;
       public          postgres    false    216    261    4838            7           2606    68392 !   usuariorolaplicacion cons_fkidrol    FK CONSTRAINT     ~   ALTER TABLE ONLY public.usuariorolaplicacion
    ADD CONSTRAINT cons_fkidrol FOREIGN KEY (fkidrol) REFERENCES public.rol(id);
 K   ALTER TABLE ONLY public.usuariorolaplicacion DROP CONSTRAINT cons_fkidrol;
       public          postgres    false    4879    252    261            &           2606    68407 (   estado_idea estado_idea_codigo_idea_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.estado_idea
    ADD CONSTRAINT estado_idea_codigo_idea_fkey FOREIGN KEY (codigo_idea) REFERENCES public.idea(codigo_idea) ON UPDATE CASCADE ON DELETE CASCADE;
 R   ALTER TABLE ONLY public.estado_idea DROP CONSTRAINT estado_idea_codigo_idea_fkey;
       public          postgres    false    238    230    4860            '           2606    68412 (   estado_idea estado_idea_id_estado_i_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.estado_idea
    ADD CONSTRAINT estado_idea_id_estado_i_fkey FOREIGN KEY (id_estado_i) REFERENCES public.estado_i(id_estado_i) ON UPDATE CASCADE ON DELETE CASCADE;
 R   ALTER TABLE ONLY public.estado_idea DROP CONSTRAINT estado_idea_id_estado_i_fkey;
       public          postgres    false    228    230    4850            (           2606    68417 =   estado_oportunidad estado_oportunidad_codigo_oportunidad_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.estado_oportunidad
    ADD CONSTRAINT estado_oportunidad_codigo_oportunidad_fkey FOREIGN KEY (codigo_oportunidad) REFERENCES public.oportunidad(codigo_oportunidad) ON UPDATE CASCADE ON DELETE CASCADE;
 g   ALTER TABLE ONLY public.estado_oportunidad DROP CONSTRAINT estado_oportunidad_codigo_oportunidad_fkey;
       public          postgres    false    234    246    4871            )           2606    68422 6   estado_oportunidad estado_oportunidad_id_estado_o_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.estado_oportunidad
    ADD CONSTRAINT estado_oportunidad_id_estado_o_fkey FOREIGN KEY (id_estado_o) REFERENCES public.estado_o(id_estado_o) ON UPDATE CASCADE ON DELETE CASCADE;
 `   ALTER TABLE ONLY public.estado_oportunidad DROP CONSTRAINT estado_oportunidad_id_estado_o_fkey;
       public          postgres    false    4854    232    234            0           2606    71541    oportunidad fk_foco_innovacion    FK CONSTRAINT     �   ALTER TABLE ONLY public.oportunidad
    ADD CONSTRAINT fk_foco_innovacion FOREIGN KEY (id_foco_innovacion) REFERENCES public.foco_innovacion(id_foco_innovacion) ON DELETE CASCADE;
 H   ALTER TABLE ONLY public.oportunidad DROP CONSTRAINT fk_foco_innovacion;
       public          postgres    false    4858    246    236            1           2606    71546    oportunidad fk_tipo_innovacion    FK CONSTRAINT     �   ALTER TABLE ONLY public.oportunidad
    ADD CONSTRAINT fk_tipo_innovacion FOREIGN KEY (id_tipo_innovacion) REFERENCES public.tipo_innovacion(id_tipo_innovacion) ON DELETE CASCADE;
 H   ALTER TABLE ONLY public.oportunidad DROP CONSTRAINT fk_tipo_innovacion;
       public          postgres    false    246    4883    256            *           2606    68427 !   idea idea_id_foco_innovacion_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.idea
    ADD CONSTRAINT idea_id_foco_innovacion_fkey FOREIGN KEY (id_foco_innovacion) REFERENCES public.foco_innovacion(id_foco_innovacion) ON UPDATE CASCADE ON DELETE CASCADE;
 K   ALTER TABLE ONLY public.idea DROP CONSTRAINT idea_id_foco_innovacion_fkey;
       public          postgres    false    4858    238    236            +           2606    68432 !   idea idea_id_tipo_innovacion_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.idea
    ADD CONSTRAINT idea_id_tipo_innovacion_fkey FOREIGN KEY (id_tipo_innovacion) REFERENCES public.tipo_innovacion(id_tipo_innovacion) ON UPDATE CASCADE ON DELETE CASCADE;
 K   ALTER TABLE ONLY public.idea DROP CONSTRAINT idea_id_tipo_innovacion_fkey;
       public          postgres    false    4883    256    238            ,           2606    68437 *   idea_usuario idea_usuario_codigo_idea_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.idea_usuario
    ADD CONSTRAINT idea_usuario_codigo_idea_fkey FOREIGN KEY (codigo_idea) REFERENCES public.idea(codigo_idea) ON UPDATE CASCADE ON DELETE CASCADE;
 T   ALTER TABLE ONLY public.idea_usuario DROP CONSTRAINT idea_usuario_codigo_idea_fkey;
       public          postgres    false    4860    238    240            -           2606    68442 ,   idea_usuario idea_usuario_email_usuario_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.idea_usuario
    ADD CONSTRAINT idea_usuario_email_usuario_fkey FOREIGN KEY (email_usuario) REFERENCES public.usuario(email) ON UPDATE CASCADE ON DELETE CASCADE;
 V   ALTER TABLE ONLY public.idea_usuario DROP CONSTRAINT idea_usuario_email_usuario_fkey;
       public          postgres    false    4887    240    260            .           2606    68447 >   informacion_adicional informacion_adicional_usuario_email_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.informacion_adicional
    ADD CONSTRAINT informacion_adicional_usuario_email_fkey FOREIGN KEY (usuario_email) REFERENCES public.usuario(email) ON DELETE CASCADE;
 h   ALTER TABLE ONLY public.informacion_adicional DROP CONSTRAINT informacion_adicional_usuario_email_fkey;
       public          postgres    false    4887    242    260            /           2606    68462 >   login_perfil login_perfil_usuario_id_8cfa6ed3_fk_usuario_email    FK CONSTRAINT     �   ALTER TABLE ONLY public.login_perfil
    ADD CONSTRAINT login_perfil_usuario_id_8cfa6ed3_fk_usuario_email FOREIGN KEY (usuario_id) REFERENCES public.usuario(email) DEFERRABLE INITIALLY DEFERRED;
 h   ALTER TABLE ONLY public.login_perfil DROP CONSTRAINT login_perfil_usuario_id_8cfa6ed3_fk_usuario_email;
       public          postgres    false    260    244    4887            2           2606    68472 ?   oportunidad_usuario oportunidad_usuario_codigo_oportunidad_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.oportunidad_usuario
    ADD CONSTRAINT oportunidad_usuario_codigo_oportunidad_fkey FOREIGN KEY (codigo_oportunidad) REFERENCES public.oportunidad(codigo_oportunidad) ON UPDATE CASCADE ON DELETE CASCADE;
 i   ALTER TABLE ONLY public.oportunidad_usuario DROP CONSTRAINT oportunidad_usuario_codigo_oportunidad_fkey;
       public          postgres    false    248    246    4871            3           2606    68477 :   oportunidad_usuario oportunidad_usuario_email_usuario_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.oportunidad_usuario
    ADD CONSTRAINT oportunidad_usuario_email_usuario_fkey FOREIGN KEY (email_usuario) REFERENCES public.usuario(email) ON UPDATE CASCADE ON DELETE CASCADE;
 d   ALTER TABLE ONLY public.oportunidad_usuario DROP CONSTRAINT oportunidad_usuario_email_usuario_fkey;
       public          postgres    false    260    4887    248            4           2606    68497     perfil perfil_usuario_email_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.perfil
    ADD CONSTRAINT perfil_usuario_email_fkey FOREIGN KEY (usuario_email) REFERENCES public.usuario(email) ON DELETE CASCADE;
 J   ALTER TABLE ONLY public.perfil DROP CONSTRAINT perfil_usuario_email_fkey;
       public          postgres    false    260    250    4887            :           2606    71614 )   proyecto proyecto_id_foco_innovacion_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.proyecto
    ADD CONSTRAINT proyecto_id_foco_innovacion_fkey FOREIGN KEY (id_foco_innovacion) REFERENCES public.foco_innovacion(id_foco_innovacion);
 S   ALTER TABLE ONLY public.proyecto DROP CONSTRAINT proyecto_id_foco_innovacion_fkey;
       public          postgres    false    267    236    4858            ;           2606    71609 )   proyecto proyecto_id_tipo_innovacion_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.proyecto
    ADD CONSTRAINT proyecto_id_tipo_innovacion_fkey FOREIGN KEY (id_tipo_innovacion) REFERENCES public.tipo_innovacion(id_tipo_innovacion);
 S   ALTER TABLE ONLY public.proyecto DROP CONSTRAINT proyecto_id_tipo_innovacion_fkey;
       public          postgres    false    4883    256    267            8           2606    71594 )   solucion solucion_id_foco_innovacion_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.solucion
    ADD CONSTRAINT solucion_id_foco_innovacion_fkey FOREIGN KEY (id_foco_innovacion) REFERENCES public.foco_innovacion(id_foco_innovacion);
 S   ALTER TABLE ONLY public.solucion DROP CONSTRAINT solucion_id_foco_innovacion_fkey;
       public          postgres    false    265    236    4858            9           2606    71589 )   solucion solucion_id_tipo_innovacion_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.solucion
    ADD CONSTRAINT solucion_id_tipo_innovacion_fkey FOREIGN KEY (id_tipo_innovacion) REFERENCES public.tipo_innovacion(id_tipo_innovacion);
 S   ALTER TABLE ONLY public.solucion DROP CONSTRAINT solucion_id_tipo_innovacion_fkey;
       public          postgres    false    256    265    4883            �   d   x�3��,.I�MTHIUpO-.�<�9�vI-N�-H=�1�3�݅��:ϼ2/=193?/��ؓ����2�J �0��������|�y\1z\\\ ��<R      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �   �   x���MN�0�מS��v�T�bQ	�-�Q2�\9��6�8g��M����}���h֞�(�0��u'��p��{�z�d���"���K3��,	l�r���f�>�3w3�0��e.��`�������ڶ�Y.06�꼣�� q��:D3ŧ��*]���P\F��-L��py�U��o?}��2��	����8O�RT��D�����*�k x�e�Y      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �   �   x��=�0@�9>E�va�� 0 ���ʒ:Ve��+;��G�����:�4Ӡ1S�Ya�y¢�� ������H�Y
�Tۇ�k$c�T'CġF!8�����c�͉�w����"�s�gL���1��-<W �g6%      �   �  x��R�O�0~v���T��R�Fi�Q$��T@Ӥ�I�b��i~tk����f�b%�Ow��w����� ��37�.-J����ڕ�=Ex">	�0��V1�ֲ`��<�\��t4�g#��\�m�j �N+�41�Ӳ̈́9~MUw��`+���H��*V:�v�IS��W�I��պ`Bz�.P�� ��D{�޶ ��Ү��9u�XC§Q��iq�ԏ��tUq}d1�(���Sd�=�%�����J�����#e�����듚�>�������H��B����ҘJ(0j��:�D���/P���\׃vnn'� ��<�"��&��l:{ x/�'Q�3Y�,�O�����XּM���u�B���ŪUj���fg���.�a�^^��\��L��0�h�ۦM�W�(��ؐ�y��:ځ�����]�UB{����W
��W-O�K|��d�	�p_5�$3�5ĚeB+^'�&'&�;��V�/�q����@-      �      x������ � �      �   .  x���1R�0Ek�{Od'�@Rm�y�(#k5+��p���!��p�@����_6���	C-�iZt��ܪ-I�΢u�� ����{B	.4Y`˽$��<�Á��u����50�@�:����5���\���fI;J(�ޏ�> D�-���Ż���Qc�	r�Gh(u�|��p>�'�T��W�_�_ϒ�k����ѳ�6�E��8���En2��t�ƨ(}���Ԩ�����iUꇴT�D*�Ye}�<�{X�o>N�a���w��y�,��ug�*b���g5��}��~�
�      �   �   x�u���0D�ۯ��3����ěW�^6�!5P�_D%%�u���\9M��f	#m\A��g��56�zj{�]��2p�9!'?�+������K@�*U@ƂxZq�x��p�^svY��JC��1�}�f�[=�V�L����ǜ�u�d�[��z � \�      �   0  x���=n� ��� �/c�)K�.��5�IK���XJ��3���j;qS�N�d��<~zz������e�C�����!v�T��P-ԛF��Ể�2QU��IJxkt�g�)_� $�dD�q̄�����X/$,�{�zە�;@O���SJ«c�jB�o�2vFɱ�g"=(��B��;�[z�6�>۶���xwL�����U�vQ?\BS,��@�q��{�T�W�sjSi>�_�8,�s
�w��C@¹W��S��ǧ�dP�x���|~6�� ��9	Io|���C)�\H��~4p�O�+�$��%�      �   �  x���]O�0����A��} w �2"1�hLH�
�u�� ���""z�ɺ�,�y���&2�E�N�*!Ub@RKx���z�e�A��4�@\E!KUXg�<B��7�2���B� ߩe��F�E�Ư��]�s��If ��I�v ��5��\h�ȋ2�B*}`k����	�O˖�c1'�=OX+6�H8I��c{&��o$ۛ��Y�k|;����łA%��togY��)U���(�t�J�E�%E����@;�B3dd�4�c�����_mGVvm��v]Or9�a�v^����Dg��jP�²,���.Ӌ܆��;����m@�"K"�����`��~�7RC�L��9]��z�r�A3�ȡ:�U�2��l�9"���XPT�0-�#� �C��Bxegm5a�+�4�:=}      �      x������ � �      �   h  x����j1�����m�d��;El�,���L7�D�$ͮ��6}�>�/��u�P
	�Cf�;g$ÌVh����u�L�+&����(ڱMN�EB����0�0Em੸��.�l�0�֠�ଇ�����.�_[��y2J�pE�ZSh���˜��+�J���2�l1�C�x�=H��d+��ϲ�F�e=7������K�hEk�Y���ŏ.��))Y����:G�V`� 4�a��;q�	���?$���x�0I��L0N��ɂ%�|ak�ICDW.ǔ�^�48E��;�������s�A���e��:W�����Y�9�����!�/r��X����W�ĵ� \��%��49�߽Yܥ      �     x�Ŕ͎�0���S��=�����Ӧ	��j�m�Tj�RD�lIG�l_���또��R.U�#f�?� q�D �x;f01  {en��^r�Fa�_A�i��E�ƺ̲��%�Cc�m�M��8�,�b�Z�ƶ�Fh�`�8Z�,����n���}��	TJ�H񨄡p�v9��xc�����Q[�e�~��_֭��䫱��U�i"K~��԰�P�P�~�OVv���+J\�U{P�o�����q��h��CC&o�b��ZRrGvs�3.�u��`�K�������=�0k{:\.&��\z��p�}[����it�/�-]�P)�P��řn�4ͪ�%����*[M�.��a�Zm�t�� ����t�I�SI�~g$nS{>��f\ьk��� `��=�yT[O=E�Ϫ o\m�t���@�y���װ)��hnP�:ϥ�_�����.�%ו�h���N�]�
��U��d�DVyOd����X]z޹+����i@��;�����n�      �   1   x�3�tL����,.)JL�/�2�t�(H-*��2�-.M,������� ��      �   �   x�����0D��+:��*vB)L�؁�E.�JJ��"�@�:Og?�$�(�B������8���pf�`s�n�]���*��c�<r�eT����ʦ���(�ȥ��������m�V2�V_���5���r�z�/�6ݶ	:��#���QH�      �   �  x�͘Kr�8���)x���h<y��b!$�BRT2s�������MД_r��8���Avl���)؄�:�>��0��
C���M�|3���v��[���.,Kc�}��hq�f?�Dk��h-/O�1��
�cH9�F��b#��� >qW	��0�-�RWba�pH�:R�T��蟧݅q�W��ݶ_B������S�O.$ O���W����X,��qi����ro�|��}�>�+d{���'+����m����لO��_�_�4O�H�����,��A3D�R-,z��d��Uy�̆��wnxZ����\��#v�Sp)̣� IR|�́62�ݾip�0�L�^ގ�wilvi� V�5�5��P`���('v�>�R�!(CNj���T@�I�Z	�1g��Lp�ɏ�xH�����M�{&SK�87ֹ�$>�bRkK��5��`���L9�dF��iv�{�y�S�./���E������P�)���	�4����]-�F���HJS'$� ƕ.b?J�h(urLw� H˱�b�����s #C�G?\mݴ4�*�pƍ��L��1�P,n@���H�s��g��$���<��w/�)+ �+��L�㢤��R����)M����]�~*'�:�g9���\�zR՚'�Ol���Kw;��&H2��a�m�Ob��/�[eA;̙�he	.W���<w�*]P�z(ԇ,m]�>B�F��V��\bF1��HEja��$�턶MӢ�8HQL�p���5ai�z��|��O�i���M5L?�*P�Y �2gd;g>�����Y�x�����oÖ́��xΆ�֐=;��JPn��d7�z���c��Ai��0zĺ{��T��,��Y�����.�ߒ��}j�ҕ4�ZQw�ɵ,~#/�K��Жr����@���vuu�4���      �   5   x�3���K.J�M�+I��2�JL�L�L8C����r�3��B1z\\\ �{0      �      x������ � �      �   �  x���I����ǩ_�̬\�W�T`Ӛ�t��D�i�7���J����Ĝ!�o�}�^���2�%}�=o�k���/��2��=���7+���0��EU�����$��ᧁ��WS�`4mZ����[Wb�7%��n������g�����e~\���PF�_�W��|��'�}�8� �W|����NK��27�g��F �~���.�6��n��Ҕ��@�����5X���)�O�x����� �wTYg�$���ov����a��O��9C�����$��A��r�i��1����	��#>`��H��	 �;50�˵VJQ3�g4��wE���T�߸^S��ղA��t�}�4��E-�.2�R�~��'>0#�Լ��g���G>�4U	�vؼ�0���B�%������wG� .:����0���`8
c8�CLF�ۤ��x��9�T�v}&�/,�Y�gk�{Q�i �Q�|5�WU���#���sr�_*�zI�O�[��z�2����R���)�s��M�;�������{S {�:��ơ�W����5��tyǻ�Q�>�G��
Z�u�Na��������
L���V�#�"e���U$9�z�;o���a���?#�յ�itɖ��L��0Cy�u��B22qp���3sl|̣֔Kv
D��'d��W�����(���/��K=�/]��Y�5ov��F��Gy�ڇ���Z��*���v./x���Q����7�+=�'��?��@ �OAm�&�pL�w�L���Ym���T��	4T���,�"�Z�3}�(g\K��kV�te����q^D!�' �0��R(��\ʴL���~�۾O��K9G���X�W��1YY.3tk�+����h���sd��ꒉ{�7�Isf#ػ}��
��F����Q)�����.��B�Ɛ��F�C���8e+R��5@�[Lb��ɁFB���[��#�T��$��aKQŒ'(��[Uz-�G�BU<ۦw&�������>���w����w���5�f
k]�����2#�r�v^h��xD�Ү:e�����`�{��X�7��q�_�\%��5�=�s�q��Ӌ$��ha3AH黼��>�����d�%0"6�cA3����.:�>�f}�R	�2�K%���?Y���m�H݅%yڎM[����a��Ʊ(GK��.�`�_p�������j���,��c���,��BT�a���i�Bk���J�q���\������L���g���n/T�H&b��v�
%��JE8��/Y�,�	-o�v��U�TYt%�q���[ڼ)��R=`��f��M:��=����Q�%T�#�X�������cf0�I}��*[4"O�`�%��8�0u�]�Y3��9)�n���ʃ�W��-\7����ǯ�y����(����-�N��M��*wϷ��LW�[�F¤GRr
�=n_�����_����Yђ���%A�7��p	9_Ҍ{����}}�BY@Kuۍ̒�]^i�;\q��K����T|W<^��_�ѕd���8�1��;TY2"�r��CVГXjs��vo������99\�@%9$;;�1�x����"�u��RJ���V��EE�,�$����i�ۺ?{��G��gɚO�P	VdK�R��H�u���l��.��:r:�+�u���.ܫ}X{����߾}�����      �      x������ � �     